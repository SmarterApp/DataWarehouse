'''
Define measurement and logging for new UDL's internal benchmarking.
Mostly using techniques from decorators in python

Created on June 10, 2013

Main Method: measure_cpu_time(function_to_be_decorated)
Main method: measure_elapsed_time(function_to_be_decorated)
Main method: measure_cpu_plus_elapsed_time(function_to_be_decorated)

@author: ejen
'''
import inspect
import math
import imp
import time
import datetime

from udl2_util.database_util import connect_db, execute_queries
from udl2.defaults import UDL2_DEFAULT_CONFIG_PATH_FILE
from preetl import create_queries as queries
from udl2 import message_keys as mk

try:
    config_path_file = os.environ['UDL2_CONF']
except Exception:
    config_path_file = UDL2_DEFAULT_CONFIG_PATH_FILE

udl2_conf = imp.load_source('udl2_conf', config_path_file)
from udl2_conf import udl2_conf


def remove_celery_system_frame_objects(frames):
    '''
    a function that removes frame objects that is part of celery system. So we keep only UDL2 related calling
    @param frames: a list of frames names
    @type frames: list
    '''
    udl2_frames = [f for f in frames if '/celery/' not in f and '<frozen ' not in f and '/billiard/' not in f and '/kombu/' not in f and 'measurement.py:_wrapped' not in f and
                   '/celery:<module>' not in f]
    return udl2_frames


def measure_cpu_time(fn, quiet=udl2_conf['quiet_mode']):
    '''
    a decorator measure cpu process time for executing fn and print out the result to standard output
    @param fn: function that are to be executed
    @type fn: a funtion in python
    '''
    def _wrapped(*args, **kwargs):
        if quiet:
            return fn(*args, **kwargs)
        else:
            start_cpu_time = time.clock()
            result = fn(*args, **kwargs)
            end_cpu_time = time.clock()
            current_frame = inspect.currentframe()
            outer_frames = inspect.getouterframes(current_frame, 1)
            frames = [fn.__name__] + [of[1] + ':' + of[3] for of in outer_frames]
            frames = remove_celery_system_frame_objects(frames)
            print("MEASURE-- cpu time {time:.10f} seconds for executing {module:s}.{function:s}".format(time=(end_cpu_time - start_cpu_time),
                                                                                                        module=fn.__module__,
                                                                                                        function=fn.__name__,))
            return result
    return _wrapped


def measure_elapsed_time(fn, quiet=udl2_conf['quiet_mode']):
    '''
    a decorator measure elasped time for executing fn and print out the result to standard output
    @param fn: function that are to be executed
    @type fn: a funtion in python
    '''
    def _wrapped(*args, **kwargs):
        if quiet:
            return fn(*args, **kwargs)
        else:
            start_time = time.time()
            result = fn(*args, **kwargs)
            end_time = time.time()
            current_frame = inspect.currentframe()
            outer_frames = inspect.getouterframes(current_frame, 1)
            frames = [fn.__name__] + [of[1] + ':' + of[3] for of in outer_frames]
            frames = remove_celery_system_frame_objects(frames)
            print("MEASURE-- elapsed time {time:.10f} seconds for executing {module:s}.{function:s}".format(time=(end_time - start_time),
                                                                                                            module=fn.__module__,
                                                                                                            function=fn.__name__,))
            return result
    return _wrapped


def measure_cpu_plus_elasped_time(fn, quiet=udl2_conf['quiet_mode']):
    '''
    a decorator measure elasped time for executing fn and print out the result to standard output
    @param fn: function that are to be executed
    @type fn: a funtion in python
    '''
    def _wrapped(*args, **kwargs):
        if quiet:
            return fn(*args, **kwargs)
        else:
            start_time = time.time()
            start_clock = time.clock()
            result = fn(*args, **kwargs)
            end_clock = time.clock()
            end_time = time.time()
            current_frame = inspect.currentframe()
            outer_frames = inspect.getouterframes(current_frame, 1)
            frames = [fn.__name__] + [of[1] + ':' + of[3] for of in outer_frames]
            frames = remove_celery_system_frame_objects(frames)
#             print(("MEASURE-- " +
#                   #" call stack: {frame}, " +
#                   " cpu time: {ctime:.10f} seconds, elapsed time: {etime:.10f} seconds " +
#                   " for executing {module:s}.{function:s}, args: {args},kwargs: {kwargs}").format(frame=" <== ".join(frames),
#                                                                                                  etime=(end_time - start_time),
#                                                                                                  module=fn.__module__,
#                                                                                                  ctime=(end_clock - start_clock),
#                                                                                                  function=fn.__name__,
#                                                                                                  args=args,
#                                                                                                  kwargs=kwargs))
            return result
    return _wrapped


def show_amount_of_data_affected(fn, quiet=udl2_conf['quiet_mode']):
    '''
    a decorator to print normalized message for amount of data to be moved
    @param fn: function that are to be executed
    @type fn: a funtion in python that return amount of data be moved, it returns a dictionary with following fields {amount: number of data,
            unit: measure unit, module: where the code module is, function: what function is used}
    '''
    def _wrapped(*args, **kwargs):
        if quiet:
            return fn(*args, **kwargs)
        else:
            result = fn(*args, **kwargs)
            current_frame = inspect.currentframe()
            outer_frames = inspect.getouterframes(current_frame, 1)
            frames = [fn.__name__] + [of[1] + ':' + of[3] for of in outer_frames]
            frames = remove_celery_system_frame_objects(frames)
#             print(("MEASURE--  call stack: {frame}, " +
#                   "{amount:s} {unit:s} are {action:s} by {module:s}.{function:s}").format(frame=" <== ".join(frames),
#                                                                                           amount=str(result['amount']),
#                                                                                           unit=result['unit'],
#                                                                                           action=result['action'],
#                                                                                           module=result['module'],
#                                                                                           function=result['function']))
#             return result
    return _wrapped


def describe_tasks(fn):
    pass


def benchmarking_udl2(func):
    '''
    Decorator for benchmarking UDL2 stages (Worker level, and be updated to use for all levels)
    '''
    def wrapper_func(*args, **kwargs):
        start_time = datetime.datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.datetime.now()
        # add guid batch
        result[mk.GUID_BATCH] = args[0][mk.GUID_BATCH]
        # add load_type
        result[mk.LOAD_TYPE] = args[0][mk.LOAD_TYPE]
        # add phase name
        result[mk.UDL_PHASE] = str(func.__module__) + '.' + str(func.__name__) + ' ' + result.get(mk.UDL_PHASE, '')
        # insert result into batch table
        record_benchmark_in_batch_table(start_time, end_time, result)
        return result
    return wrapper_func


def record_benchmark(start_time, end_time, batch_guid, load_type, udl_phase, **optional_columns):
    '''
    Record the benchmarking data in the batch table

    @param start_time: The time the task began
    @param end_time: The ending time of the task
    @param batch_guid: The guid for the current batch
    @param load_type: The type of the files being loaded. ie. Assessment
    @param udl_phase: the name of the phase/task being benchmarked
    @param optional_columns: optional columns as kwargs:
        optional_columns should be in the list: [working_schema, size_records, size_units, phase_status, udl_phase_step
                                                 udl_leaf=False, task_id, task_status_url, user_email]
        note: If the batch table is updated this list will need to be updated
    '''

    result = {mk.GUID_BATCH: batch_guid,
              mk.LOAD_TYPE: load_type,
              mk.UDL_PHASE: udl_phase,
              }
    result.update(optional_columns)
    # loop over the keys and only update the result dict if the key is in the expected list of keys and the value is not none

    record_benchmark_in_batch_table(start_time, end_time, result)


def record_benchmark_in_batch_table(start_time, end_time, result):
    '''
    Record a benchmarking result into batch table
    '''
    # TODO: can use try-except
    if result is None:
        return

    # add time
    duration = end_time - start_time
    result[mk.DURATION] = str(duration)
    result[mk.START_TIMESTAMP] = str(start_time)
    result[mk.END_TIMESTAMP] = str(end_time)
    # add status, by default is SUCCESS
    if mk.UDL_PHASE_STEP_STATUS not in list(result.keys()):
        result[mk.UDL_PHASE_STEP_STATUS] = mk.SUCCESS
    # add udl_leaf, by default is False
    if mk.UDL_LEAF not in list(result.keys()):
        result[mk.UDL_LEAF] = False

    # TODO: calculate two columns: time_for_one_million_records, records_per_hour
    """
    if mk.SIZE_RECORDS in result.keys():
        try:
            result[mk.TIME_FOR_ONE_MILLION_RECORDS] = str(1000000 * duration / int(result[mk.SIZE_RECORDS]))
            result[mk.RECORDS_PER_HOUR] = math.ceil(3600 * int(result[mk.SIZE_RECORDS]) / (duration.microseconds * 1000000))

            # a = str(1000000 * duration / int(result[mk.SIZE_RECORDS]))
            # b = math.ceil(3600 * int(result[mk.SIZE_RECORDS]) / (duration.microseconds * 1000000))
            print("********", result[mk.TIME_FOR_ONE_MILLION_RECORDS], result[mk.RECORDS_PER_HOUR], result[mk.SIZE_RECORDS], duration)
        except ValueError:
            print("*************", result[mk.SIZE_RECORDS], duration.seconds, duration)
    """

    # insert into batch table
    #from udl2_util.database_util import connect_db, execute_queries

    insert_query = queries.insert_batch_row_query(udl2_conf['udl2_db']['staging_schema'], udl2_conf['udl2_db']['batch_table'], **result)

    # create database connection
    (conn, _engine) = connect_db(udl2_conf['udl2_db']['db_driver'],
                                 udl2_conf['udl2_db']['db_user'],
                                 udl2_conf['udl2_db']['db_pass'],
                                 udl2_conf['udl2_db']['db_host'],
                                 udl2_conf['udl2_db']['db_port'],
                                 udl2_conf['udl2_db']['db_database'])
    # insert into batch table
    execute_queries(conn, [insert_query], 'Exception in record_benchmark_in_batch_table, execute query to insert into batch table', 'measurement', 'record_benchmark_in_batch_table')
    conn.close()


class BatchTableBenchmark(object):
    '''
    Class for maintaining the information required to populate the batch table
    '''

    def __init__(self, guid_batch, load_type, udl_phase, start_timestamp, end_timestamp, working_schema=None, size_records=None, size_units=None,
                 udl_phase_step_status=mk.SUCCESS, udl_phase_step=None, udl_leaf=False, task_id=None, task_status_url=None, user_email=None, user_sid=None):
        '''Constructor'''
        self.guid_batch = guid_batch
        self.load_type = load_type
        self.udl_phase = udl_phase
        self.start_timestamp = str(start_timestamp)
        self.end_timestamp = str(end_timestamp)
        self.duration = str(end_timestamp - start_timestamp)
        self.working_schema = working_schema
        self.size_records = size_records
        self.size_units = size_units
        self.udl_phase_step_status = udl_phase_step_status
        self.udl_phase_step = udl_phase_step
        self.udl_leaf = udl_leaf
        self.task_id = task_id
        self.task_status_url = task_status_url
        self.user_email = user_email
        self.user_sid = user_sid

    def get_result_dict(self):
        '''
        Get a dictionary containing all instance attributes that are not None
        '''
        return {col: val for col, val in self.__dict__.items() if val is not None}

    def record_benchmark(self):
        '''
        Record the benchmark information for the this instance of the benchmarking information
        '''
        result = self.get_result_dict()
        insert_query = queries.insert_batch_row_query(udl2_conf['udl2_db']['staging_schema'], udl2_conf['udl2_db']['batch_table'], **result)

        # create database connection
        (conn, _engine) = connect_db(udl2_conf['udl2_db']['db_driver'],
                                     udl2_conf['udl2_db']['db_user'],
                                     udl2_conf['udl2_db']['db_pass'],
                                     udl2_conf['udl2_db']['db_host'],
                                     udl2_conf['udl2_db']['db_port'],
                                     udl2_conf['udl2_db']['db_database'])
        # insert into batch table
        execute_queries(conn, [insert_query], 'Exception in record_benchmark_in_batch_table, execute query to insert into batch table', 'measurement', 'record_benchmark_in_batch_table')
        conn.close()
