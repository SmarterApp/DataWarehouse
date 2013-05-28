from __future__ import absolute_import
from udl2.celery import celery
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from udl2_util import file_util
from udl2_util import file_util
import filesplitter.file_splitter as file_splitter
import udl2.message_keys as mk
import time
import os


logger = get_task_logger(__name__)


@celery.task(name="udl2.W_file_splitter.task")
def task(incoming_msg):
    '''
    This is the celery task for splitting file
    '''
    # parse the message
    # expanded_msg = parse_initial_message(incoming_msg)

    start_time = time.time()

    # Get necessary params for file_splitter
    lzw = incoming_msg[mk.LANDING_ZONE_WORK_DIR]
    jc = incoming_msg[mk.JOB_CONTROL]
    batch_id = jc[1]
    parts = incoming_msg[mk.PARTS]

    expanded_dir = file_util.get_expanded_dir(lzw, batch_id)
    # TODO: Refactor this, its messy.
    csv_file = None
    for file_name in os.listdir(expanded_dir):
        if file_util.extract_file_ext(file_name) == '.csv':
            csv_file = os.path.join(expanded_dir, file_name)
            break

    subfiles_dir = get_subfiles_dir(lzw, batch_id)
    file_util.create_directory(subfiles_dir)

    # do actual work of splitting file
    split_file_tuple_list, header_file_path = file_splitter.split_file(csv_file, parts=parts,
                                                                       output_path=subfiles_dir)

    finish_time = time.time()
    spend_time = int(finish_time - start_time)

    logger.info(task.name)
    logger.info("FILE_SPLITTER: Split <%s> into %i sub-files in %i" % (csv_file, parts, spend_time))

    # for each of sub file, call loading task
    for split_file_tuple in split_file_tuple_list:
        message_for_file_loader = generate_msg_for_file_loader(expanded_msg, split_file_tuple, header_file_path)
        udl2.W_file_loader.task.apply_async([message_for_file_loader], queue='Q_files_to_be_loaded', routing_key='udl2')

    return split_file_tuple_list


# TODO: Create a generic function that creates any of the (EXPANDED,ARRIVED,SUBFILES) etc. dirs in separate util file.
def get_subfiles_dir(lzw, batch_id):
    subfiles_dir = os.path.join(lzw, batch_id, 'SUBFILES')
    return subfiles_dir


def generate_msg_for_file_loader(split_file_tuple, header_file_path, lzw, jc, fdw_conf, staging_conf):
    # TODO: It would be better to have a dict over a list, we can access with key instead of index - more clear.
    split_file_path = split_file_tuple[0]
    split_file_line_count = split_file_tuple[1]
    split_file_row_start = split_file_tuple[2]

    file_loader_msg = {}
    file_loader_msg[mk.FILE_TO_LOAD] = split_file_path
    file_loader_msg[mk.LINE_COUNT] = split_file_line_count
    file_loader_msg[mk.ROW_START] = split_file_row_start
    file_loader_msg[mk.HEADER_FILE] = header_file_path
    file_loader_msg[mk.LANDING_ZONE_WORK_DIR] = lzw
    file_loader_msg[mk.JOB_CONTROL] = jc
    file_loader_msg[mk.APPLY_RULES] = False
    file_loader_msg[mk.FDW_CONF] = fdw_conf
    file_loader_

    return file_loader_msg


@celery.task(name="udl2.W_file_splitter.error_handler")
def error_handler(uuid):
    result = AsyncResult(uuid)
    exc = result.get(propagate=False)
    print('Task %r raised exception: %r\n%r' % (
          exc, result.traceback))


'''
def parse_initial_message(msg):
    # Read input msg. If it contains any key defined in FILE_SPLITTER_CONF, use the value in msg.
    # Otherwise, use value defined in FILE_SPLITTER_CONF
    params = udl2.celery.FILE_SPLITTER_CONF

    if ROW_LIMIT in msg.keys():
        params[ROW_LIMIT] = msg[ROW_LIMIT]
    if PARTS in msg.keys():
        params[PARTS] = msg[PARTS]
    if WORK_ZONE in msg.keys():
        params[WORK_ZONE] = msg[WORK_ZONE]
    if LANDING_ZONE_FILE in msg.keys():
        params[LANDING_ZONE_FILE] = msg[LANDING_ZONE_FILE]
    if HISTORY_ZONE in msg.keys():
        params[HISTORY_ZONE] = msg[HISTORY_ZONE]
    if KEEP_HEADERS in msg.keys():
        params[KEEP_HEADERS] = msg[KEEP_HEADERS]
    if LANDING_ZONE in msg.keys():
        params[LANDING_ZONE] = msg[LANDING_ZONE]
    if BATCH_ID in msg.keys():
        params[BATCH_ID] = msg[BATCH_ID]
    return params
'''