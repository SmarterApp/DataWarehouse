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

__author__ = 'nestep'

"""
This module contains the logic to write to an assessment item-level CSV extract file.
"""

import csv
import logging
import copy

from edcore.database.edcore_connector import EdCoreDBConnection
from edcore.utils.file_utils import generate_path_to_item_csv
from edextract.status.constants import Constants
from edextract.status.status import ExtractStatus, insert_extract_stats
from edextract.tasks.constants import Constants as TaskConstants, QueryType
from edextract.utils.file_utils import File
from edextract.utils.metadata_reader import MetadataReader
from edextract.exceptions import NotFileException

logger = logging.getLogger('edextract')

ITEM_KEY_POS = 0
# Write the header to the file
# TODO: Should not be hard coded
CSV_HEADER = ['key', 'studentId', 'segmentId', 'position', 'clientId', 'operational', 'isSelected',
              'format', 'score', 'scoreStatus', 'adminDate', 'numberVisits', 'strand', 'contentLevel',
              'pageNumber', 'pageVisits', 'pageTime', 'dropped']


def generate_items_csv(tenant, output_files, task_info, extract_args):
    '''
    Write item-level data to CSV file

    @param tenant: Requestor's tenant ID
    @param output_files: List of output file path's for item extract
    @param task_info: Task information for recording stats
    @param extract_args: Arguments specific to generate_items_csv
    '''
    # Get stuff
    query = extract_args[TaskConstants.TASK_QUERIES][QueryType.QUERY]
    items_root_dir = extract_args[TaskConstants.ROOT_DIRECTORY]
    item_ids = extract_args[TaskConstants.ITEM_IDS]

    with EdCoreDBConnection(tenant=tenant) as connection:
        # Get results (streamed, it is important to avoid memory exhaustion)
        results = connection.get_streaming_result(query, fetch_size=10240)

        _append_csv_files(items_root_dir, item_ids, results, output_files, CSV_HEADER)
        # Done
        insert_extract_stats(task_info, {Constants.STATUS: ExtractStatus.EXTRACTED})


def _check_file_for_items(file_descriptor, item_ids):
    csv_reader = csv.reader(file_descriptor, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    for row in csv_reader:
        if row[ITEM_KEY_POS] in item_ids:
            return True
    return False


def _append_csv_files(items_root_dir, item_ids, results, output_files, csv_header):

    def open_outfile(output_file):
        logging.info('creating output_file[' + output_file + ']')
        _file = open(output_file, 'w')
        csvwriter = csv.writer(_file, quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(csv_header)
        return _file

    _output_files = copy.deepcopy(output_files)
    if type(_output_files) is not list:
        _output_files = [_output_files]
    logging.info('preparing file list')
    files, total_file_size = _prepare_file_list(items_root_dir, results)
    number_of_files = len(_output_files)
    threshold_size = -1
    if number_of_files > 1:
        threshold_size = int(total_file_size / len(_output_files))

    out_file = None
    for file in files:
        # Write this file to output file if we are not checking for specific item IDs or if this file contains
        # at least one of the requested item IDs
        with open(file.name, 'r') as in_file:
            if item_ids is None or _check_file_for_items(in_file, item_ids):
                in_file.seek(0)
                if out_file is not None and threshold_size > 0 and out_file.tell() + file.size > threshold_size and _output_files:
                    # close current out_file
                    out_file.close()
                    out_file = None
                if out_file is None:
                    output_file = _output_files.pop(0)
                    out_file = open_outfile(output_file)
                out_file.write(in_file.read())

    if out_file is not None:
        out_file.close()
    logging.info('all archived csv files are generated')


def _prepare_file_list(items_root_dir, results):
    # Read file size from metadata reader
    metadata_reader = MetadataReader()
    files = []
    total_size = 0
    for result in results:
        path = generate_path_to_item_csv(items_root_dir, **result)
        # Get the file size of the file from metadata file
        size = metadata_reader.get_size(path)
        if size is -1:
            raise NotFileException(path + ' does not exist')
        file = File(path, size)
        total_size += size
        files.append(file)
    return files, total_size
