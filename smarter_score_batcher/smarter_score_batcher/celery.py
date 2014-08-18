'''
Created on Jul 29, 2014

@author: tosako
'''
from edworker.celery import setup_celery as setup_for_worker, configure_celeryd


PREFIX = 'smarter_score_batcher.celery'


def setup_celery(settings, prefix=PREFIX):
    '''
    Setup celery based on parameters defined in setting (ini file).
    This calls by client application when dictionary of settings is given

    :param settings:  dict of configurations
    :param prefix: prefix in configurations used for configuring celery
    '''
    setup_for_worker(celery, settings, prefix)


# Create an instance of celery, check if it's for prod celeryd mode and configure it for prod mode if so
celery, conf = configure_celeryd(PREFIX, prefix=PREFIX)