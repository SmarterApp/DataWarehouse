'''
This module contains exception classes used in EdApi

Created on Jan 18, 2013

@author: dip
'''
from pyramid.httpexceptions import HTTPNotFound
from edapi.httpexceptions import generate_exception_response


class EdApiError(Exception):
    '''
    a general EdApi error.
    '''
    def __init__(self, msg):
        '''
        :param msg: the error message.
        :type msg: string
        '''
        self.msg = msg


class ReportNotFoundError(EdApiError):
    '''
    a custom exception raised when a report cannot be found.
    '''
    def __init__(self, name):
        '''
        :param name: the report's name
        :type name: string
        '''
        self.msg = "Report %s is not found" % name


class InvalidParameterError(EdApiError):
    '''
    a custom exception raised when a report parameter is not found.
    '''
    def __init__(self, msg=None):
        '''
        :param msg: the error message.
        :type msg: string
        '''
        if msg is None:
            self.msg = "Invalid Parameters"
        else:
            self.msg = msg


class ForbiddenError(EdApiError):
    '''
    a custom exception raised when access is denied to a report
    '''
    def __init__(self, msg=None):
        '''
        :param msg: the error message.
        :type msg: string
        '''
        if msg is None:
            self.msg = "Forbidden Access"
        else:
            self.msg = msg


class NotFoundException(HTTPNotFound):
    '''
    a custom http exception return when resource not found
    '''
    #code = 404
    #title = 'Requested report not found'
    #explanation = ('The resource could not be found.')

    def __init__(self, msg):
        '''
        :param msg: the error message.
        :type msg: string
        '''
        super().__init__(**generate_exception_response(msg))
