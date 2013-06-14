'''
Created on May 9, 2013

@author: tosako
'''
from celery.app import defaults
import ast
from celery.utils import strtobool


# default timeout 20 seconds
TIMEOUT = 20
# default number of pdf generation retries
RETRIES = 1
# minimum file size of pdf generated
MINIMUM_FILE_SIZE = 80000


def get_celeryconfig(settings, prefix='celery'):
    '''
    Returns celery configuration from setting dict.
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
    return convert_to_celery_options(celery_config)


def get_config(settings, prefix='celery'):
    '''
    Sets timeout for subprocess call in task and return Celery config
    '''
    setup_global_settings(settings)
    # load celery config
    celery_config = get_celeryconfig(settings, prefix)
    return celery_config


def setup_global_settings(settings):
    '''
    Setup global settings for pdf tasks
    '''
    global TIMEOUT
    global MINIMUM_FILE_SIZE
    global RETRIES
    TIMEOUT = int(settings.get('pdf.generate.timeout', TIMEOUT))
    MINIMUM_FILE_SIZE = int(settings.get('pdf.minimum.file.size', MINIMUM_FILE_SIZE))
    RETRIES = int(settings.get('pdf.retries.allowed', RETRIES))


def convert_to_celery_options(config):
    '''
    Converts string representation of configuration to its expected data type
    '''
    type_map = {'any': ast.literal_eval,
                'int': int,
                'string': str,
                'bool': strtobool,
                'float': float,
                'dict': ast.literal_eval,
                'tuple': ast.literal_eval,
                'list': ast.literal_eval
                }

    mapping = {}

    # Read from celery.app.defaults to get the expected data type for each configuarable property
    for (key, value) in defaults.flatten(defaults.NAMESPACES):
        __type = type_map[value.type]
        if __type:
            mapping[key] = __type

    # For each config that need to configure, cast/convert to the expected data type
    for (key, value) in config.items():
        if mapping[key]:
            config[key] = mapping[key](value)
    return config
