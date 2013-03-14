'''
Created on Mar 13, 2013

@author: tosako
'''
import venusian
import pyramid
from functools import wraps


class report_config(object):
    '''
    used for processing decorator '@report_config' in pyramid scans
    '''
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __call__(self, original_func):
        settings = self.__dict__.copy()

        def callback(scanner, name, obj):
            def wrapper(*args, **kwargs):
                return original_func(self, *args, **kwargs)
            scanner.config.add_report_config((obj, original_func), **settings)
        venusian.attach(original_func, callback, category='edapi')
        return original_func


def user_info(orig_func):
    '''
    Append user_info to the returning result
    '''
    @wraps(orig_func)
    def wrap(*args, **kwds):
        results = orig_func(*args, **kwds)
        principals = pyramid.security.effective_principals(pyramid.threadlocal.get_current_request())
        if principals is not None:
            for principal in principals:
                if type(principal) == dict:
                    results['user_info'] = principal
                    break
        return results
    return wrap
