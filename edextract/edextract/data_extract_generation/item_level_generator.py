__author__ = 'nestep'

"""
This module contains the logic to write to an assessment item-level CSV extract file.
"""

import csv
import logging
import os

from edcore.database.edcore_connector import EdCoreDBConnection
from edextract.status.constants import Constants
from edextract.status.status import ExtractStatus, insert_extract_stats
from edextract.tasks.constants import Constants as TaskConstants, QueryType

logger = logging.getLogger(__name__)

ITEM_KEY_POS = 0
# Write the header to the file
# TODO: Should not be hard coded
CSV_HEADER = ['key', 'student_guid', 'segmentId', 'position', 'clientId', 'operational', 'isSelected',
              'format', 'score', 'scoreStatus', 'adminDate', 'numberVisits', 'strand', 'contentLevel',
              'pageNumber', 'pageVisits', 'pageTime', 'dropped']

def generate_items_csv(tenant, output_files, task_info, extract_args):
    """
    Write item-level data to CSV file

    @param tenant: Requestor's tenant ID
    @param output_files: List of output file path's for item extract
    @param task_info: Task information for recording stats
    @param extract_args: Arguments specific to generate_items_csv
    """
    # Get stuff
    query = extract_args[TaskConstants.TASK_QUERIES][QueryType.QUERY]
    items_root_dir = extract_args[TaskConstants.ROOT_DIRECTORY]
    item_ids = extract_args[TaskConstants.ITEM_IDS]
    threshold_size = extract_args.get(TaskConstants.THRESHOLD_SIZE, -1)

    with EdCoreDBConnection(tenant=tenant) as connection:
        # Get results (streamed, it is important to avoid memory exhaustion)
        results = connection.get_streaming_result(query)

        _append_csv_files(items_root_dir, item_ids, results, output_files[0], CSV_HEADER, threshold_size)
        # Done
        insert_extract_stats(task_info, {Constants.STATUS: ExtractStatus.EXTRACTED})


def _get_path_to_item_csv(items_root_dir, state_code=None, asmt_year=None, asmt_type=None, effective_date=None, asmt_subject=None, asmt_grade=None, district_guid=None, student_guid=None):
    path = items_root_dir
    if state_code is not None:
        path = os.path.join(path, state_code)
    else:
        return path
    if asmt_year is not None:
        path = os.path.join(path, asmt_year)
    else:
        return path
    if asmt_type is not None:
        path = os.path.join(path, asmt_type.upper().replace(' ', '_'))
    else:
        return path
    if effective_date is not None:
        path = os.path.join(path, effective_date)

    if asmt_subject is not None:
        path = os.path.join(path, asmt_subject.upper())
    else:
        return path
    if asmt_grade is not None:
        path = os.path.join(path, asmt_grade)
    else:
        return path
    if district_guid is not None:
        path = os.path.join(path, district_guid)
    else:
        return path
    if student_guid is not None:
        path = os.path.join(path, student_guid + '.csv')
    return path


def _check_file_for_items(file_descriptor, item_ids):
    csv_reader = csv.reader(file_descriptor, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    for row in csv_reader:
        if row[ITEM_KEY_POS] in item_ids:
            return True
    return False


def _append_csv_files(items_root_dir, item_ids, results, output_file, csv_header, threshold_size):

    def open_outfile():
        out_file = open(output_file, 'w')
        csvwriter = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(csv_header)
        return out_file

    out_file = open_outfile()
    file_number = 0
    for result in results:
        # Build path to file
        path = _get_path_to_item_csv(items_root_dir, **result)
        # Write this file to output file if we are not checking for specific item IDs or if this file contains
        # at least one of the requested item IDs
        if os.path.exists(path):
            in_file = open(path, 'r')
            if not item_ids is not None or _check_file_for_items(in_file, item_ids):
                if threshold_size > 0:
                    # we want to limit file size for output file.
                    in_file_size = os.fstat(in_file.fileno()).st_size
                    if in_file_size + out_file.tell() > threshold_size:
                        # close current out_file and write in new file
                        out_file.close()
                        _rename_to_partial_filename(output_file, file_number)
                        file_number += 1
                        out_file = open_outfile()
                in_file.seek(0)
                out_file.write(in_file.read())
            in_file.close()
    out_file.close()
    if file_number is not 0:
        _rename_to_partial_filename(path, file_number)


def _rename_to_partial_filename(src, file_number):
    dir_name, base_name = os.path.split(src)
    partial_dir = os.path.join(dir_name, 'partial', "%03d" % file_number)
    os.makedirs(partial_dir, mode=0o700, exist_ok=True)
    new_name = "%03d%s" % (file_number, base_name)
    os.rename(src, os.path.join(partial_dir, new_name))
