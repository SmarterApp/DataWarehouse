'''
Celery Tasks for data extraction

Created on Nov 5, 2013

@author: ejen
'''
import os
import sys
import csv
import logging
import subprocess
import platform
from edextract.celery import celery
from edextract.exceptions import ExtractionError
import copy
from edextract.celery import TIMEOUT
import services
from celery.exceptions import MaxRetriesExceededError
from edcore.database.stats_connector import StatsDBConnection
from edextract.extract_status import insert_extract_stats
from edcore.database.edcore_connector import EdCoreDBConnection

OK = 0
FAIL = 1

log = logging.getLogger('smarter')


@celery.task(name="tasks.extract.handle_request",
             max_retries=services.celery.MAX_RETRIES,
             default_retry_delay=services.celery.RETRY_DELAY)
def handle_request(cookie=None, task_queries=None, output_uri=None):
    '''
    '''
    celery_result = is_available.delay(query=task_queries[0])
    if celery_result.get():
        generate_csv(query=task_queries[1]).delay()
        return True
    else:
        return False


@celery.task(name="tasks.extract.is_available",
             max_retries=services.celery.MAX_RETRIES,
             default_retry_delay=services.celery.RETRY_DELAY)
def is_available(cookie=None, check_query=None):
    '''
    '''
    print('execute tasks.extract.is_available')
    with EdCoreDBConnection() as connection:
        result = connection.execute(check_query).fetchone()
    if len(result) >= 1:
        return True
    else:
        return False


@celery.task(name="tasks.extract.generate_csv",
             max_retries=services.celery.MAX_RETRIES,
             default_retry_delay=services.celery.RETRY_DELAY)
def generate_csv(cookie=None, extract_query=None, output_uri=None):
    '''
    '''
    print('execute tasks.extract.generate_csv')
    EdCoreDBConnection
    with EdCoreDBConnection() as connection:
        result = connection.execute(extract_query).fetchone()
    if len(result) >= 1:
        return True
    else:
        return False
