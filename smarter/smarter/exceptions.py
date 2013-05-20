'''
Created on May 20, 2013

@author: dip
'''


class SmarterError(Exception):
    '''
    a general EdApi error.
    '''
    def __init__(self, msg):
        '''
        @param msg: the error message.
        @type msg: string
        '''
        self.msg = msg


class PdfGenerationError(SmarterError):
    '''
    a custom exception raised when a pdf generation failed
    '''
    def __init__(self):
        self.msg = "Pdf Generation failed "
