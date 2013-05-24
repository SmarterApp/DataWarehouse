'''
Created on May 10, 2013

@author: dawu
'''
import os
import sys
import logging
import subprocess
from services.celeryconfig import TIMEOUT
import platform
from services.celery import celery
from services.exceptions import PdfGenerationError
import copy

pdf_procs = ['wkhtmltopdf']
pdf_defaults = ['--enable-javascript', '--page-size', 'Letter', '--print-media-type', '-l', '--javascript-delay', '6000', '--footer-center', 'Page [page] of [toPage]', '--footer-font-size', '9']

OK = 0
FAIL = 1


@celery.task(name='tasks.generate_pdf')
def generate_pdf(cookie, url, outputfile, options=pdf_defaults, timeout=TIMEOUT, cookie_name='edware', grayScale=False, mkdir_mode=0o700):
    '''
    Generates pdf from given url. Returns exist status code from shell command.
    We set up timeout in order to terminate pdf generating process, for wkhtmltopdf 0.10.0 doesn't exit
    properly upon successfully completion (see wkhtmltopdf ISSUE 141). TIMEOUT can be removed if that bug is fixed in future.
    '''
    try:
        # Only for windows environment, set shell to true
        shell = False
        if platform.system() == 'Windows':
            shell = True
        prepare_file_path(file_path=outputfile,mkdir_mode=mkdir_mode)
        wkhtmltopdf_option = copy.deepcopy(options)
        if grayScale:
            wkhtmltopdf_option += ['-g']
        wkhtmltopdf_option += ['--cookie', cookie_name, cookie, url, outputfile]
        return subprocess.call(pdf_procs + wkhtmltopdf_option, timeout=timeout, shell=shell)
    except subprocess.TimeoutExpired:
        # check output file, return 0 if file is created successfully
        isSucceed = os.path.exists(outputfile) and os.path.getsize(outputfile)
        return OK if isSucceed else FAIL
    except:
        log = logging.getLogger(__name__)
        log.error("Generate PDF error: %s", sys.exc_info())
        return FAIL


@celery.task(name='tasks.get_pdf')
def get_pdf(cookie, url, outputfile, options=pdf_defaults, timeout=TIMEOUT, cookie_name='edware', grayScale=False, mkdir_mode=0o700):
    '''
    Reads pdf file if it exists, else it'll request to generate pdf.  Returns byte stream from generated pdf file
    '''

    if not os.path.exists(outputfile):
        generate_task = generate_pdf(cookie, url, outputfile, options=pdf_defaults, timeout=timeout, cookie_name=cookie_name, grayScale=grayScale, mkdir_mode=mkdir_mode)
        if generate_task is FAIL:
            raise PdfGenerationError()

    with open(outputfile, 'rb') as file:
        stream = file.read()
    return stream


def prepare_file_path(file_path, mkdir_mode=0o700):
    if os.path.exists(os.path.dirname(file_path)) is not True:
        os.makedirs(os.path.dirname(file_path), mkdir_mode)
