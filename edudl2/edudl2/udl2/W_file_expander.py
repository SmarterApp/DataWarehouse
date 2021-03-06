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

from __future__ import absolute_import
from celery.utils.log import get_task_logger
import datetime
from edudl2.udl2.celery import celery
from edudl2.udl2.udl2_base_task import Udl2BaseTask
from edudl2.fileexpander.file_expander import expand_file
from edudl2.udl2_util.measurement import BatchTableBenchmark
from edudl2.udl2 import message_keys as mk

__author__ = 'sravi'

'''
File Expander Worker for the UDL Pipeline.
The decrypted file at zones/landing/work/<TENANT>/<TS_GUID_BATCH>/decrypted/ is expanded
and written to zones/landing/work/<TENANT>/<TS_GUID_BATCH>/expanded/

The output of this worker will serve as the input to the subsequent worker [W_simple_file_validator].
'''

logger = get_task_logger(__name__)


@celery.task(name="udl2.W_file_expander.task", base=Udl2BaseTask)
def task(incoming_msg):
    """
    This is the celery task to expand the decrypted file
    """
    start_time = datetime.datetime.now()

    # Retrieve parameters from the incoming message
    file_to_expand = incoming_msg[mk.FILE_TO_EXPAND]
    guid_batch = incoming_msg[mk.GUID_BATCH]
    tenant_directory_paths = incoming_msg[mk.TENANT_DIRECTORY_PATHS]
    expand_to_dir = tenant_directory_paths[mk.EXPANDED]
    load_type = incoming_msg[mk.LOAD_TYPE]

    logger.info('W_FILE_EXPANDER: expand file <%s> with guid_batch = <%s> to directory <%s>' % (file_to_expand, guid_batch, expand_to_dir))
    file_contents = expand_file(file_to_expand, expand_to_dir)
    logger.info('W_FILE_EXPANDER: expanded files:  <%s>' % (', '.join(file_contents)))

    finish_time = datetime.datetime.now()

    # Benchmark
    benchmark = BatchTableBenchmark(guid_batch, load_type, task.name, start_time, finish_time, task_id=str(task.request.id), tenant=incoming_msg[mk.TENANT_NAME])
    benchmark.record_benchmark()

    # Outgoing message to be piped to the file expander
    outgoing_msg = {}
    outgoing_msg.update(incoming_msg)
    return outgoing_msg
