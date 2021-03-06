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

'''
Created on Nov 4, 2013

@author: dip
'''
from edworker.celery import setup_celery as setup, configure_celeryd,\
    get_config_file
from hpz_client.frs.config import initialize as initialize_hpz

# default timeout 60 seconds
TIMEOUT = 60
# default number of pdf generation retries
MAX_RETRIES = 1
# minimum file size of pdf generated
MINIMUM_FILE_SIZE = 80000
# pdfunite timeout
PDFUNITE_TIMEOUT = 3000

# javascript delay default
JAVASCRIPT_DELAY = 6000

# delay in retry. Default to 5 seconds
RETRY_DELAY = 5
PREFIX = 'services.celery'


def setup_celery(settings, prefix=PREFIX):
    '''
    Setup celery based on parameters defined in setting (ini file).
    This calls by client application when dictionary of settings is given

    :param settings:  dict of configurations
    :param prefix: prefix in configurations used for configuring celery
    '''
    setup(celery, settings, prefix)
    setup_global_settings(settings)


def setup_global_settings(settings):
    '''
    Setup global settings for pdf tasks

    :param settings:  dict of configurations
    '''
    global TIMEOUT
    global MINIMUM_FILE_SIZE
    global MAX_RETRIES
    global RETRY_DELAY
    global PDFUNITE_TIMEOUT
    global JAVASCRIPT_DELAY
    TIMEOUT = int(settings.get('pdf.generate_timeout', TIMEOUT))
    MINIMUM_FILE_SIZE = int(settings.get('pdf.minimum_file_size', MINIMUM_FILE_SIZE))
    MAX_RETRIES = int(settings.get('pdf.retries_allowed', MAX_RETRIES))
    RETRY_DELAY = int(settings.get('pdf.retry_delay', RETRY_DELAY))
    PDFUNITE_TIMEOUT = int(settings.get('pdf.merge.pdfunite_timeout', PDFUNITE_TIMEOUT))
    JAVASCRIPT_DELAY = int(settings.get('pdf.wkhtmltopdf.javascript_delay', JAVASCRIPT_DELAY))

# Create an instance of celery, check if it's for prod celeryd mode and configure it for prod mode if so
celery, conf = configure_celeryd(PREFIX, prefix=PREFIX)
prod_config = get_config_file()
if prod_config:
    setup_global_settings(conf)
    initialize_hpz(conf)
