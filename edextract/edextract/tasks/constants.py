'''
Created on Dec 9, 2013

@author: dip
'''


class ExtractType():
    CSV = 'csv'
    JSON = 'json'


class ReportType():
    STATISTICS = 'statistics'
    COMPLETION = 'completion'


class Constants():
    TASK_IS_JSON_REQUEST = 'is_json_request'
    TASK_TASK_ID = 'task_id'
    CELERY_TASK_ID = 'celery_task_id'
    TASK_FILE_NAME = 'file_name'
    TASK_QUERY = 'query'
    DEFAULT_QUEUE_NAME = 'extract'
    SYNC_QUEUE_NAME = 'extract_sync'
    ARCHIVE_QUEUE_NAME = 'extract_archve'
    TENANT = 'tenant'
    STATE_CODE = 'state_code'
    ACADEMIC_YEAR = 'academicYear'
    REPORT_TYPE = 'report_type'
