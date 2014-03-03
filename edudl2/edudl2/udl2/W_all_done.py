'''
Created on Sep 10, 2013

@author: swimberly
'''
import datetime
from celery.utils.log import get_task_logger
from edudl2.udl2 import message_keys as mk
from edudl2.udl2.celery import celery
from edudl2.udl2_util.measurement import BatchTableBenchmark
from edudl2.udl2.udl2_base_task import Udl2BaseTask
from edcore.database.utils.constants import UdlStatsConstants
from edcore.database.utils.query import update_udl_stats
from edcore.utils.utils import merge_dict


logger = get_task_logger(__name__)


def report_udl_batch_metrics_to_log(msg, end_time, pipeline_status):
    logger.info('UDL Batch Summary:')
    logger.info('Batch Guid: ' + msg[mk.GUID_BATCH])
    logger.info('Batch Status: ' + pipeline_status)
    logger.info('Start time: ' + str(msg[mk.START_TIMESTAMP]))
    logger.info('End time: ' + str(end_time))
    if mk.INPUT_FILE_SIZE in msg:
        logger.info('Input file size: ' + str(round(msg[mk.INPUT_FILE_SIZE] / (1024 * 1024.0), 3)) + 'MB')
    if mk.TOTAL_ROWS_LOADED in msg:
        logger.info('Total Records Processed: ' + str(msg[mk.TOTAL_ROWS_LOADED]))


def report_batch_to_udl_stats(msg, end_time, status):
    logger.info('Reporting to UDL daily stats')
    stats = {}
    # TODO: it's always zero
    stats[UdlStatsConstants.RECORD_LOADED_COUNT] = msg[mk.TOTAL_ROWS_LOADED] if mk.TOTAL_ROWS_LOADED in msg else 0
    load_status = UdlStatsConstants.STATUS_INGESTED if status is mk.SUCCESS else UdlStatsConstants.STATUS_FAILED
    update_udl_stats(msg[mk.GUID_BATCH], merge_dict(stats, {UdlStatsConstants.LOAD_END: end_time, UdlStatsConstants.LOAD_STATUS: load_status}))


@celery.task(name='udl2.W_all_done.task', base=Udl2BaseTask)
def task(msg):
    start_time = msg[mk.START_TIMESTAMP]
    end_time = datetime.datetime.now()
    load_type = msg[mk.LOAD_TYPE]
    guid_batch = msg[mk.GUID_BATCH]

    # infer overall pipeline_status based on previous pipeline_state
    pipeline_status = mk.FAILURE if mk.PIPELINE_STATE in msg and msg[mk.PIPELINE_STATE] == 'error' else mk.SUCCESS

    benchmark = BatchTableBenchmark(guid_batch, load_type, 'UDL_COMPLETE',
                                    start_time, end_time, udl_phase_step_status=pipeline_status)
    benchmark.record_benchmark()

    # record batch stats to udl stats table
    # this will be used by migration script to move the data from pre-prod to prod
    report_batch_to_udl_stats(msg, end_time, pipeline_status)
    # report the batch metrics in Human readable format to the UDL log
    report_udl_batch_metrics_to_log(msg, end_time, pipeline_status)
    return msg
