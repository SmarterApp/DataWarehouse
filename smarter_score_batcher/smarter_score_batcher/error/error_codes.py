# (c) 2014 The Regents of the University of California. All rights reserved,
# subject to the license below.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0. Unless required by
# applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

'''
Created on Sep 24, 2014

@author: tosako
'''


class ErrorCode():
    # TSB Error codes 4xxx.
    GENERAL_TSB_ERROR = 4000

    # File Lock error code 41xx
    GENERAL_FILELOCK_ERROR = 4100
    FILE_FOR_FILELOCK_DOES_NOT_EXIST = 4110

    # Metadata error code 42xx
    GENERAL_METADATA_ERROR = 4200
    DIRECTORY_NOT_EXIST_FOR_METADATA_GENERATOR = 4210

    # CSV related error 43xx
    CSV_GENERATE_ERROR = 4300
    CSV_PARSE_ERROR = 4310

    # Metadata related error 44xx
    UNABLE_TO_LOAD_METADATA_SUBJECT = 4400

    # File monitor related error 45xx
    GENERAL_FILE_MONITOR_ERROR = 4500
    FILE_NOT_FOUND_FILE_MONITOR_ERROR = 4510

    # Security error
    PATH_TRAVERSAL_DETECTED = 4600

    message = {GENERAL_TSB_ERROR: 'GENERAL_TSB_ERROR',
               GENERAL_FILELOCK_ERROR: 'GENERAL_FILELOCK_ERROR',
               FILE_FOR_FILELOCK_DOES_NOT_EXIST: 'FILE_FOR_FILELOCK_DOES_NOT_EXIST',
               GENERAL_METADATA_ERROR: 'GENERAL_METADATA_ERROR',
               DIRECTORY_NOT_EXIST_FOR_METADATA_GENERATOR: 'DIRECTORY_NOT_EXIST_FOR_METADATA_GENERATOR',
               CSV_GENERATE_ERROR: 'CSV_GENERATE_ERROR',
               CSV_PARSE_ERROR: 'CSV_PARSE_ERROR',
               UNABLE_TO_LOAD_METADATA_SUBJECT: 'UNABLE_TO_LOAD_METADATA_SUBJECT',
               PATH_TRAVERSAL_DETECTED: 'PATH_TRAVERSAL_DETECTED'}


class ErrorSource():
    # Unable to find identify source
    FROM_EXCEPTION_STACK = 0

    METADATA_GENERATOR_TOP_DOWN = 4001
    METADATA_GENERATOR_BOTTOM_UP = 4002
    LOCK_AND_WRITE = 4003
    GENERATE_CSV_FROM_XML = 4004
    METADATATEMPLATEMANAGER_GET_TEMPLATE = 4005
    MOVE_TO_STAGE = 4006
    GENERATE_PERFORMANCE_METADATA = 4007
    PREPARE_ASSESSMENT_DIR = 4008
    REMOTE_CSV_GENERATOR = 4009
    REMOTE_WRITE = 4010

    message = {METADATA_GENERATOR_TOP_DOWN: 'metadata_generator_top_down',
               METADATA_GENERATOR_BOTTOM_UP: 'metadata_generator_bottom_up',
               LOCK_AND_WRITE: 'lock_and_write',
               GENERATE_CSV_FROM_XML: 'generate_csv_from_xml',
               METADATATEMPLATEMANAGER_GET_TEMPLATE: 'MetadataTemplateManager.get_template',
               MOVE_TO_STAGE: 'move_to_stage',
               GENERATE_PERFORMANCE_METADATA: 'generate_performance_metadata',
               PREPARE_ASSESSMENT_DIR: 'prepare_assessment_dir',
               REMOTE_CSV_GENERATOR: 'remote_csv_generator',
               REMOTE_WRITE: 'remote_write'
               }
