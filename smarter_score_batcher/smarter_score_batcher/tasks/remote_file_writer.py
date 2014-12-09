'''
Created on Jul 28, 2014

@author: tosako
'''


import logging
from smarter_score_batcher.celery import celery, conf
from smarter_score_batcher.utils.file_utils import file_writer, create_path
from smarter_score_batcher.utils.meta import extract_meta_names
from edcore.utils.file_utils import generate_path_to_item_csv, generate_file_path
from smarter_score_batcher.tasks.remote_csv_writer import remote_csv_generator
import time
from smarter_score_batcher.error.exceptions import TSBException,\
    TSBSecurityException
import os
from smarter_score_batcher.error.error_codes import ErrorCode, ErrorSource
from smarter_score_batcher.tasks.remote_metadata_writer import metadata_generator_task

logger = logging.getLogger("smarter_score_batcher")


@celery.task(name="tasks.tsb.remote_file_writer")
def remote_write(xml_data):
    '''
    save data in given path
    :returns: True when file is written
    '''
    written = False
    try:
        meta_names = extract_meta_names(xml_data)
        root_dir_csv = conf.get("smarter_score_batcher.base_dir.csv")
        if root_dir_csv is not None:
            root_dir_csv = os.path.abspath(root_dir_csv)
        root_dir_xml = conf.get("smarter_score_batcher.base_dir.xml")
        if root_dir_xml is not None:
            root_dir_xml = os.path.abspath(root_dir_xml)
        timestamp = time.strftime('%Y%m%d%H%M%S', time.gmtime())
        xml_file_path = create_path(root_dir_xml, meta_names, generate_file_path, **{'extension': timestamp + '.xml'})
        if os.path.commonprefix([root_dir_xml, xml_file_path]) != root_dir_xml:
            raise TSBSecurityException(msg='Fail to create filepath name requested dir[' + xml_file_path + ']', err_code=ErrorCode.PATH_TRAVERSAL_DETECTED, err_source=ErrorSource.REMOTE_WRITE)
        written = file_writer(xml_file_path, xml_data)
        if written:
            work_dir = conf.get("smarter_score_batcher.base_dir.working")
            if work_dir is not None:
                work_dir = os.path.abspath(work_dir)
            queue_name = conf.get('smarter_score_batcher.async_queue')
            csv_file_path = create_path(root_dir_csv, meta_names, generate_path_to_item_csv)
            if os.path.commonprefix([root_dir_csv, csv_file_path]) != root_dir_csv:
                raise TSBSecurityException(msg='Fail to create filepath name requested dir[' + csv_file_path + ']', err_code=ErrorCode.PATH_TRAVERSAL_DETECTED, err_source=ErrorSource.REMOTE_WRITE)
            metadata_queue = conf.get('smarter_score_batcher.metadata_queue')
            # Fire two celery tasks - one to generate metadata for xml, and one to generate item level/assessment csv
            metadata_generator_task.apply_async(args=(xml_file_path,), queue=metadata_queue)    # @UndefinedVariable
            remote_csv_generator.apply_async(args=(meta_names, csv_file_path, xml_file_path, work_dir, metadata_queue), queue=queue_name)  # @UndefinedVariable
    except TSBException as e:
        # ignore exception for error handling because this function is synchonous call
        logging.error(str(e))
    return written
