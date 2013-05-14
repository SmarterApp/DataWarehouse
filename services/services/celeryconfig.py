'''
Created on May 9, 2013

@author: tosako
'''
from services.celery import celery

# default timeout 20 seconds
TIMEOUT = 20


def setup_celery(settings, prefix='celery'):
    celery_config = load_config(settings, prefix)
    celery.config_from_object(celery_config)


def load_celeryconfig(settings, prefix):
    '''
    Loads celery configuration from setting dict.
    Any value whose corresponding key starts with prefix and followed by a period
    is considered as celery configuration.
    Configuration key will be stored in uppercase as celery's convention.
    '''
    # load celery config
    celery_config = {}
    prefix = prefix + "."
    # get config values
    for key in settings:
        if key.startswith(prefix):
            celery_key = key[len(prefix):].upper()
            celery_config[celery_key] = settings[key]
    return celery_config


def load_config(settings, prefix='celery'):
    # load pdf generation timeout
    global TIMEOUT
    TIMEOUT = settings.get('pdf.generate.timeout', TIMEOUT)
    # load celery config
    celery_config = load_celeryconfig(settings, prefix)
    return celery_config
