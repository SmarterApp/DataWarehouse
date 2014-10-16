from __future__ import absolute_import
from celery.utils.log import get_task_logger
import datetime
from edudl2.udl2.celery import celery
from edudl2.udl2 import message_keys as mk
from edudl2.udl2.udl2_base_task import Udl2BaseTask
from edudl2.get_load_type.get_load_type import get_load_type
from edudl2.udl2_util.measurement import BatchTableBenchmark
from edudl2.udl2_util.util import get_assessment_type
from edcore.database.utils.constants import UdlStatsConstants
from edudl2.udl2.constants import Constants
from edcore.database.utils.query import update_udl_stats_by_batch_guid
__author__ = 'tshewchuk'

logger = get_task_logger(__name__)


@celery.task(name="udl2.W_get_load_type.task", base=Udl2BaseTask)
def task(incoming_msg):
    start_time = datetime.datetime.now()
    guid_batch = incoming_msg.get(mk.GUID_BATCH)
    tenant_directory_paths = incoming_msg.get(mk.TENANT_DIRECTORY_PATHS)
    expanded_dir = tenant_directory_paths.get(mk.EXPANDED)

    load_type = get_load_type(expanded_dir)

    logger.info('W_GET_LOAD_TYPE: Load type is <%s>' % load_type)
    end_time = datetime.datetime.now()

    # benchmark
    benchmark = BatchTableBenchmark(guid_batch, load_type, task.name, start_time, end_time, task_id=str(task.request.id),
                                    tenant=incoming_msg.get(mk.TENANT_NAME))
    benchmark.record_benchmark()

    # Outgoing message to be piped to the file validator
    outgoing_msg = {}
    outgoing_msg.update(incoming_msg)
    outgoing_msg.update({mk.LOAD_TYPE: load_type})
    if load_type == Constants.LOAD_TYPE_ASSESSMENT:
        assessment_type = get_assessment_type(expanded_dir)
        outgoing_msg.update({mk.ASSESSMENT_TYPE: assessment_type})
    # Update UDL stats
    update_udl_stats_by_batch_guid(guid_batch, {UdlStatsConstants.LOAD_TYPE: load_type})
    return outgoing_msg
