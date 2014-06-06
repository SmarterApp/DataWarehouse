from celery import Task, chain
from edudl2.udl2 import message_keys as mk
import edudl2.udl2 as udl2
from edcore.database.utils.constants import UdlStatsConstants
from edcore.database.utils.query import update_udl_stats
from edudl2.exceptions.udl_exceptions import UDLException
__author__ = 'sravi'
from celery.utils.log import get_task_logger
import datetime
from edudl2.udl2_util.measurement import BatchTableBenchmark


'''
Abstract base celery task for all udl2 tasks. Every UDL2 task should be based on this

example usage: @celery.task(name="udl2.W_file_decrypter.task", base=Udl2BaseTask)

Responsible for supporting generic task features like Error handling and post task work if any
This being an abstract class, it wont be registered as a celery task, but will be used as the base class for all udl2 tasks
more about abstract class at: http://docs.celeryproject.org/en/latest/userguide/tasks.html#abstract-classes
'''
logger = get_task_logger(__name__)


class Udl2BaseTask(Task):
    abstract = True

    def get_post_etl_error_chain(self, msg):
        tasks = {"assessment": [udl2.W_all_done.task.s(msg)],
                 "studentregistration": [udl2.W_all_done.task.s(msg),
                                         udl2.W_job_status_notification.task.s()]}
        return chain(tasks[msg[mk.LOAD_TYPE]])

    def get_all_done_error_chain(self, msg):
        if msg[mk.LOAD_TYPE] == "studentregistration":
            return chain(udl2.W_job_status_notification.task.s(msg))
        else:
            return None

    def get_default_error_chain(self, msg):
        if msg[mk.LOAD_TYPE] == "studentregistration":
            return chain(udl2.W_post_etl.task.s(msg), udl2.W_all_done.task.s(), udl2.W_job_status_notification.task.s())
        else:
            return chain(udl2.W_post_etl.task.s(msg), udl2.W_all_done.task.s())

    def __get_pipeline_error_handler_chain(self, msg, task_name):
        if task_name == 'udl2.W_post_etl.task':
            error_handler_chain = self.get_post_etl_error_chain(msg)
        elif task_name == 'udl2.W_all_done.task':
            error_handler_chain = self.get_all_done_error_chain(msg)
        elif task_name == 'udl2.W_job_status_notification.task':
            error_handler_chain = None
        else:
            error_handler_chain = self.get_default_error_chain(msg)
        return error_handler_chain

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        logger.info('Task returned: ' + task_id)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.exception('Task failed: ' + self.name + ', task id: ' + task_id)
        msg = args[0]
        guid_batch = msg.get(mk.GUID_BATCH)
        load_type = msg.get(mk.LOAD_TYPE)
        failure_time = datetime.datetime.now()
        udl_phase_step = ''
        working_schema = ''
        if isinstance(exc, UDLException):
            udl_phase_step = exc.udl_phase_step
            working_schema = exc.working_schema
        benchmark = BatchTableBenchmark(guid_batch, load_type,
                                        udl_phase=self.name,
                                        start_timestamp=failure_time,
                                        end_timestamp=failure_time,
                                        udl_phase_step=udl_phase_step,
                                        working_schema=working_schema,
                                        udl_phase_step_status=mk.FAILURE,
                                        task_id=str(self.request.id),
                                        error_desc=str(exc), stack_trace=einfo.traceback)
        benchmark.record_benchmark()

        # Write to udl stats table on exceptions
        stats_rec_id = msg.get(mk.UDL_STATS_REC_ID)
        if stats_rec_id:
            update_udl_stats(stats_rec_id, {UdlStatsConstants.LOAD_STATUS: UdlStatsConstants.UDL_STATUS_FAILED})

        # Write to ERR_LIST
        try:
            exc.insert_err_list(failure_time)
        except Exception:
            pass
        err_msg = {}
        err_msg.update(msg)
        err_msg.update({mk.PIPELINE_STATE: 'error'})

        error_handler_chain = self.__get_pipeline_error_handler_chain(err_msg, self.name)
        if error_handler_chain is not None:
            error_handler_chain.delay()

    def on_success(self, retval, task_id, args, kwargs):
        logger.info('Task completed successfully: '.format(task_id))
