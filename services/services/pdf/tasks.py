'''
Created on May 10, 2013

@author: dawu
'''
import os
import sys
import logging
import subprocess
import platform
from services.celery import celery
from services.exceptions import PdfGenerationError
import copy
from services.celeryconfig import TIMEOUT
import services
from celery.exceptions import MaxRetriesExceededError

pdf_procs = ['wkhtmltopdf']
pdf_defaults = ['--enable-javascript', '--page-size', 'Letter', '--print-media-type', '-l', '--javascript-delay', '6000', '--footer-center', 'Page [page] of [toPage]', '--footer-font-size', '9']

OK = 0
FAIL = 1

log = logging.getLogger('smarter')


@celery.task(name='tasks.pdf.generate', max_retries=services.celeryconfig.RETRIES, default_retry_delay=0)
def generate(cookie, url, outputfile, options=pdf_defaults, timeout=TIMEOUT, cookie_name='edware', grayscale=False):
    '''
    Generates pdf from given url. Returns exist status code from shell command.
    We set up timeout in order to terminate pdf generating process, for wkhtmltopdf 0.10.0 doesn't exit
    properly upon successfully completion (see wkhtmltopdf ISSUE 141). TIMEOUT can be removed if that bug is fixed in future.

    This task can be retried.  It throws MaxRetriesExceededError exception when retries have been exhausted.
    By default, it will retry once, immediately without any time delay.

    :param cookie: the cookie to pass into http request
    :param url:  the url to request for
    :param outputfile:  the path of the file to write pdf to
    :param options:  options passed into wkhtmltopdf
    :param timeout:  subprocess call timeout value
    :param cookie_name:  the name of the cookie being passed into http request
    :param grayscale: whether to generate pdf in grayscale
    '''
    force_regenerate = False
    try:
        # Only for windows environment, set shell to true
        shell = False
        if platform.system() == 'Windows':
            shell = True
        prepare_file_path(outputfile)
        wkhtmltopdf_option = copy.deepcopy(options)
        if grayscale:
            wkhtmltopdf_option += ['-g']
        wkhtmltopdf_option += ['--cookie', cookie_name, cookie, url, outputfile]
        subprocess.call(pdf_procs + wkhtmltopdf_option, timeout=timeout, shell=shell)
    except subprocess.TimeoutExpired:
        # Note that Timeout exception is valid due to wkhtmltopdf issue 141
        log.error('wkhmltopdf subprocess call timed out')
    except:
        log.error('Generate PDF error: %s', sys.exc_info())
        # Some exception happened, force to regenerate
        force_regenerate = True
    finally:
        # Validate pdf file was generated and greater than a certain size
        if not is_valid_pdf_file(outputfile) or force_regenerate:
            # If the retries throws an exception, return fail
            log.error("Pdf file validation failed.  Removing file %s. Will attempt to regenerate pdf", outputfile)
            delete_file(outputfile)

            kwargs = {'options': options, 'timeout': timeout, 'cookie_name': cookie_name, 'grayscale': grayscale}
            return generate.retry(args=[cookie, url, outputfile], kwargs=kwargs, exc=PdfGenerationError())
        else:
            return OK


@celery.task(name='tasks.pdf.get')
def get(cookie, url, outputfile, options=pdf_defaults, timeout=TIMEOUT, cookie_name='edware', grayscale=False, always_generate=False):
    '''
    Reads pdf file if it exists, else it'll request to generate pdf.  Returns byte stream from generated pdf file
    This is meant to be a synchronous call.  It waits for generate task to return.

    :param cookie: the cookie to pass into http request
    :param url:  the url to request for
    :param outputfile:  the path of the file to write pdf to
    :param options:  options passed into wkhtmltopdf
    :param timeout:  subprocess call timeout value
    :param cookie_name:  the name of the cookie being passed into http request
    :param grayscale: whether to generate pdf in grayscale
    :param always_generate: whether to always generate pdf instead of checking file system first
    '''
    if always_generate or not os.path.exists(outputfile):
        # always delete it first in case of regeneration error
        delete_file(outputfile)
        try:
            # This is a synchronous call
            generate.delay(cookie, url, outputfile, options=pdf_defaults, timeout=timeout, cookie_name=cookie_name, grayscale=grayscale).get()
        except MaxRetriesExceededError:
            log.error("Max retries exceeded in PDF Generation")
            raise PdfGenerationError()

    with open(outputfile, 'rb') as file:
        stream = file.read()

    return stream


def prepare_file_path(path):
    '''
    Create the directory if it doesn't exist

    :param path: Path of the file to create directory for
    '''
    if os.path.exists(os.path.dirname(path)) is not True:
        os.makedirs(os.path.dirname(path), 0o700)


def is_valid_pdf_file(path):
    '''
    Validate file specified in path that the file exists and is larger than a configurable expected size
    Returns True if file is valid, else False

    :param path: Path of the pdf file to validate
    '''
    return os.path.exists(path) and (os.path.getsize(path) > services.celeryconfig.MINIMUM_FILE_SIZE)


def delete_file(path):
    '''
    Delete file specified in path

    :param path: Path of the file to delete from file system
    '''
    if os.path.exists(path):
        os.remove(path)
