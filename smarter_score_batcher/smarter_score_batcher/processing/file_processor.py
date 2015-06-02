'''
Created on Aug 28, 2014

@author: tosako
'''
import os
import logging
from smarter_score_batcher.processing.assessment import get_assessment_mapping
from smarter_score_batcher.processing.assessment_metadata import get_assessment_metadata_mapping
from smarter_score_batcher.utils.item_level_utils import get_item_level_data
from smarter_score_batcher.utils.file_utils import csv_file_writer
from smarter_score_batcher.tasks.remote_metadata_writer import metadata_generator_task
from smarter_score_batcher.error.exceptions import GenerateCSVException, TSBException
from smarter_score_batcher.error.error_codes import ErrorSource, ErrorCode
from smarter_score_batcher.database.db_utils import save_assessment, \
    save_metadata, get_metadata
from smarter_score_batcher.database.tsb_connector import TSBDBConnection
import time

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


logger = logging.getLogger("smarter_score_batcher")


def process_assessment_data(root, meta):
    '''
    process assessment data
    :param root: xml root document
    '''
    # Create dir name based on state code and file name from asmt id
    asmtGuid, metadata = get_assessment_metadata_mapping(root)
    stateCode, data = get_assessment_mapping(root, metadata)
    retry = 3
    while retry != 0:
        with TSBDBConnection() as conn:
            try:
                transaction = conn.get_transaction()
                if not get_metadata(conn, asmtGuid):
                    save_metadata(conn, asmtGuid, stateCode, metadata)
                save_assessment(conn, data)
                transaction.commit()
                break
            except:
                transaction.rollback()
                time.sleep(1)
        retry -= 1
                    


def process_item_level_data(root, meta, csv_file_path):
    '''
    Get Item level data and writes it to csv files
    '''
    written = False
    data = get_item_level_data(root, meta)
    dirname = os.path.dirname(csv_file_path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname, exist_ok=True)
    with open(csv_file_path, 'w') as f:
        written = csv_file_writer(f, data)
    return written


def generate_csv_from_xml(meta, csv_file_path, xml_file_path, work_dir, metadata_queue, mode=0o700):
    '''
    Creates a csv in the given csv file path by reading from the xml file path
    :param csv_file_path: csv file path
    :param xml_file_path: xml file path
    :returns: True when csv file is generated
    '''
    written = False
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        process_assessment_data(root, meta)
        written = process_item_level_data(root, meta, csv_file_path)
        if written:
            metadata_generator_task.apply_async(args=(csv_file_path,), queue=metadata_queue)
    except ET.ParseError as e:
        # this should not be happened because we already validate against xsd
        error_msg = str(e)
        logger.error(error_msg)
        logger.error('this error may be caused because you have an old xsd?')
        raise GenerateCSVException(error_msg, err_code=ErrorCode.CSV_PARSE_ERROR, err_source=ErrorSource.GENERATE_CSV_FROM_XML)
    except TSBException as e:
        error_msg = str(e)
        logger.error(error_msg)
        if os.path.exists(csv_file_path):
            os.remove(csv_file_path)
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(error_msg)
        if os.path.exists(csv_file_path):
            os.remove(csv_file_path)
        raise GenerateCSVException(error_msg, err_code=ErrorCode.CSV_GENERATE_ERROR, err_source=ErrorSource.GENERATE_CSV_FROM_XML)

    return written
