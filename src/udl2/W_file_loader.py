from __future__ import absolute_import
from udl2.celery import celery, udl2_queues, udl2_stages
import udl2.W_final_cleanup
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from fileloader.file_loader import load_file


logger = get_task_logger(__name__)


@celery.task(name="udl2.W_file_loader.task")
def task(msg):
    file_name = msg['input_file']
    logger.info(task.name)
    logger.info('Loading file %s...' % file_name)
    load_file(file_name)
   
#    if udl2_stages[task.name]['next'] is not None:
#        next_msg = [file_name + ' passed after ' + task.name]
#        exec("task_instance = " + udl2_stages[task.name]['next']['task'])
#        task_instance.apply_async(next_msg,
#                                  udl2_queues[task.name]['queue'],
#                                  udl2_stages[task.name]['routing_key'])
    udl2.W_final_cleanup.task.apply_async([file_name + ' passed after ' + task.name],
                                           queue='Q_final_cleanup',
                                           routing_key='udl2')
    return msg


def generate_conf_for_loading(csv_file_path, header_file_path):
    conf = {
            'csv_file': csv_file_path,
            'header_file': header_file_path,
            'csv_table': 'UDL_test_data_block_of_100_records_with_datatype_errors_v3',
            'db_host': 'localhost',
            'db_port': '5432',
            'db_user': 'postgres',
            'db_name': 'fdw_test',
            'db_password': '3423346',
            'csv_schema': 'public',
            'fdw_server': 'udl_import',
            'staging_schema': 'public',
            'staging_table': 'tmp',
            'apply_rules': False
    }
    return conf


@celery.task(name="udl2.W_file_loader.error_handler")
def error_handler(uuid):
    result = AsyncResult(uuid)
    exc = result.get(propagate=False)
    print('Task %r raised exception: %r\n%r' % (
          exc, result.traceback))
