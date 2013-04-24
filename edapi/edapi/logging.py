'''
Created on Mar 5, 2013

@author: aoren, agrebneva
'''

import simplejson as json
import re
import logging
from edapi.utils import adopt_to_method_and_func
from pyramid.security import effective_principals,\
    unauthenticated_userid
from pyramid.threadlocal import get_current_request
from collections import OrderedDict
import inspect
import datetime

# arguments added here will not get logged
blacklist_args_global = ['first_name', 'last_name']


def audit_event(logger_name="audit", blacklist_args=[]):
    '''
    @param logger_name: the logger we will insert to log messages to.
    @type logger_name: string
    @param blacklist_args: a list of arguments that we purposely will not log
    @type blacklist_args: list
    '''
    log = logging.getLogger(logger_name)

    if (len(log.handlers) == 0):
        print(str.format("logger {0} is empty", logger_name))

    @adopt_to_method_and_func
    def audit_event_wrapper(original_func):
        # get the function param names
        arg_names = inspect.getargspec(original_func)[0]

        print(arg_names)
        func_name = original_func.__name__
        class_name = None
        if hasattr(original_func, '__self__'):
            class_name = original_func.__self__.__class__.__name__

        def __wrapped(*args, **kwds):
            allargs = {'callable': func_name}
            # Log the entry into the function
            if not class_name is None:
                allargs['class'] = class_name
            params = {}
            params['args'] = args

            # zip the param names with their values
            args_dict = dict(zip(arg_names, list(args)))
            params.update(kwds)
            allargs['params'] = params
            session_id = unauthenticated_userid(get_current_request())
            if not 'user_session' in allargs.keys():
                if session_id is not None:
                    allargs['session_id'] = session_id
            if not 'principals' in allargs.keys():
                allargs['principals'] = effective_principals(get_current_request())

            keys = set(args_dict.keys()) - set(blacklist_args)
            keys = keys - set(blacklist_args_global)

            logged_params = {}
            # if the params are not blacklisted, we will log them
            for key in args_dict:
                if key in keys:
                    logged_params[key] = args_dict[key]

            params['args'] = logged_params
            log.info(allargs)
            smarter_log = logging.getLogger('smarter')

            smarter_log.info(str.format('Entered {0} report, session_id = {1}', class_name, session_id))

            report_start_time = datetime.datetime.now().strftime('%s.%f')
            result = original_func(*args, **kwds)
            finish_time = datetime.datetime.now().strftime('%s.%f')
            report_duration_in_seconds = round(float(finish_time) - float(report_start_time), 3)

            smarter_log.info(str.format('Exited {0} report, generating the report took {1} seconds', class_name, report_duration_in_seconds))

            return result
        return __wrapped

    return audit_event_wrapper


class JsonDictLoggingFormatter(logging.Formatter):
    '''
    Json logging formatter
    '''

    def __init__(self, fmt=None, datefmt='%yyyymmdd %H:%M:%S'):
        '''
        @param fmt: the log format string
        @type fmt: string
        @param datefmt: specialized date formatting
        @type datefmt: string
        '''
        logging.Formatter.__init__(self, fmt, datefmt)
        self.fmt_tkn = re.compile(r'\((.*?)\)', re.IGNORECASE).findall(self._fmt)

    def format(self, record):
        '''
        Formats a log record and serializes to json
        @param record: the formatted record.
        '''
        loggable = OrderedDict()
        keys = record.__dict__
        for formatter in self.fmt_tkn:
            if formatter in keys:
                loggable[formatter] = record.__dict__[formatter]
        if self.usesTime():
            loggable['asctime'] = self.formatTime(record, self.datefmt)
        if isinstance(record.msg, dict):
            loggable['msg'] = record.msg
        return json.dumps(loggable)
