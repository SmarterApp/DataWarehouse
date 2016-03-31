# (c) 2014 Amplify Education, Inc. All rights reserved, subject to the license
# below.
#
# Education agencies that are members of the Smarter Balanced Assessment
# Consortium as of August 1, 2014 are granted a worldwide, non-exclusive, fully
# paid-up, royalty-free, perpetual license, to access, use, execute, reproduce,
# display, distribute, perform and create derivative works of the software
# included in the Reporting Platform, including the source code to such software.
# This license includes the right to grant sublicenses by such consortium members
# to third party vendors solely for the purpose of performing services on behalf
# of such consortium member educational agencies.

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
from edcore.database.utils.constants import UdlStatsConstants, LoadType
from edcore.database.utils.query import update_udl_stats_by_batch_guid
import json
from edcore.notification.constants import Constants as NotificationConstants
from edudl2.udl2_util.util import merge_to_udl2stat_notification


logger = get_task_logger(__name__)


def report_udl_batch_metrics_to_log(msg, end_time, pipeline_status):
    logger.info('UDL Batch Summary:')
    logger.info('Batch Guid: ' + msg.get(mk.GUID_BATCH))
    logger.info('Batch Status: ' + pipeline_status)
    logger.info('Start time: ' + str(msg.get(mk.START_TIMESTAMP)))
    logger.info('End time: ' + str(end_time))
    if mk.INPUT_FILE_SIZE in msg:
        logger.info('Input file size: ' + str(round(msg.get(mk.INPUT_FILE_SIZE) / (1024 * 1024.0), 3)) + 'MB')
    if mk.TOTAL_ROWS_LOADED in msg:
        logger.info('Total Records Processed: ' + str(msg.get(mk.TOTAL_ROWS_LOADED)))


def _create_stats_row(msg, end_time, status):
    stats = {}
    stats[UdlStatsConstants.LOAD_END] = end_time
    stats[UdlStatsConstants.RECORD_LOADED_COUNT] = msg.get(mk.TOTAL_ROWS_LOADED) if mk.TOTAL_ROWS_LOADED in msg else 0

    if status is NotificationConstants.SUCCESS:
        stats[UdlStatsConstants.LOAD_STATUS] = UdlStatsConstants.UDL_STATUS_INGESTED
        if msg[mk.LOAD_TYPE] == LoadType.STUDENT_REGISTRATION:
            stats[UdlStatsConstants.BATCH_OPERATION] = UdlStatsConstants.SNAPSHOT
            snapshot_criteria = {}
            snapshot_criteria['reg_system_id'] = msg.get(NotificationConstants.REG_SYSTEM_ID)
            snapshot_criteria['academic_year'] = msg.get(NotificationConstants.ACADEMIC_YEAR)
            stats[UdlStatsConstants.SNAPSHOT_CRITERIA] = json.dumps(snapshot_criteria)
    else:
        stats[UdlStatsConstants.LOAD_STATUS] = UdlStatsConstants.UDL_STATUS_FAILED

    return stats


def report_batch_to_udl_stats(msg, end_time, status):
    logger.info('Reporting to UDL daily stats')
    stats = _create_stats_row(msg, end_time, status)

    update_udl_stats_by_batch_guid(msg.get(mk.GUID_BATCH), stats)


@celery.task(name='udl2.W_all_done.task', base=Udl2BaseTask)
def task(msg):
    start_time = msg.get(mk.START_TIMESTAMP)
    end_time = datetime.datetime.now()
    load_type = msg.get(mk.LOAD_TYPE)
    guid_batch = msg.get(mk.GUID_BATCH)

    # infer overall pipeline_status based on previous pipeline_state
    pipeline_status = NotificationConstants.FAILURE if mk.PIPELINE_STATE in msg and msg.get(mk.PIPELINE_STATE) == 'error' else NotificationConstants.SUCCESS
    benchmark = BatchTableBenchmark(guid_batch, load_type, 'UDL_COMPLETE',
                                    start_time, end_time, udl_phase_step_status=pipeline_status,
                                    tenant=msg.get(mk.TENANT_NAME))
    benchmark.record_benchmark()

    # record batch stats to udl stats table
    # this will be used by migration script to move the data from pre-prod to prod
    report_batch_to_udl_stats(msg, end_time, pipeline_status)
    # report the batch metrics in Human readable format to the UDL log
    report_udl_batch_metrics_to_log(msg, end_time, pipeline_status)
    # update udl_stat for notification
    if pipeline_status == NotificationConstants.SUCCESS:
        merge_to_udl2stat_notification(guid_batch, {NotificationConstants.UDL_PHASE_STEP_STATUS: pipeline_status, NotificationConstants.UDL_PHASE: 'UDL_COMPLETE'})
    return msg
