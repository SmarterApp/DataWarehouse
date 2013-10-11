from __future__ import absolute_import
from udl2.celery import celery
from udl2 import W_load_csv_to_staging
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from udl2_util import file_util
from celery import group
import filesplitter.file_splitter as file_splitter
import udl2.message_keys as mk
import datetime
import os
from udl2_util.measurement import BatchTableBenchmark

logger = get_task_logger(__name__)


@celery.task(name="udl2.W_file_splitter.task")
def task(incoming_msg):
    '''
    This is the celery task for splitting file
    '''
    # parse the message
    # expanded_msg = parse_initial_message(incoming_msg)

    start_time = datetime.datetime.now()

    # Get necessary params for file_splitter
    guid_batch = incoming_msg[mk.GUID_BATCH]
    parts = incoming_msg[mk.PARTS]
    load_type = incoming_msg[mk.LOAD_TYPE]

    tenant_directory_paths = incoming_msg[mk.TENANT_DIRECTORY_PATHS]
    expanded_dir = tenant_directory_paths['expanded']
    csv_file = file_util.get_file_type_from_dir('.csv', expanded_dir)

    subfiles_dir = tenant_directory_paths['subfiles']
    #file_util.create_directory(subfiles_dir)

    # do actual work of splitting file
    split_file_tuple_list, header_file_path, totalrows, filesize = file_splitter.split_file(csv_file, parts=parts, output_path=subfiles_dir)

    finish_time = datetime.datetime.now()
    spend_time = finish_time - start_time

    logger.info(task.name)
    logger.info("FILE_SPLITTER: Split <%s> into %i sub-files in %s" % (csv_file, parts, spend_time))

    # Benchmark
    benchmark = BatchTableBenchmark(guid_batch, load_type, task.name, start_time, finish_time,
                                    size_records=totalrows, size_units=filesize, udl_phase_step_status=mk.SUCCESS,
                                    task_id=str(task.request.id))
    benchmark.record_benchmark()

    # Outgoing message to be piped to the parallel file loader
    outgoing_msg = {}
    outgoing_msg.update(incoming_msg)
    outgoing_msg.update({mk.SPLIT_FILE_LIST: split_file_tuple_list,
                         mk.HEADER_FILE_PATH: header_file_path,
                         mk.SIZE_RECORDS: totalrows
                         })
    return outgoing_msg


@celery.task(name="udl2.W_file_splitter.error_handler")
def error_handler(uuid):
    result = AsyncResult(uuid)
    exc = result.get(propagate=False)
    print('Task %r raised exception: %r\n%r' % (
          exc, result.traceback))
