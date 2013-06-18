from __future__ import absolute_import
from udl2.defaults import UDL2_DEFAULT_CONFIG_PATH_FILE
from celery import Celery
from kombu import Exchange, Queue
import os
import imp
from udl2_util.measurement import measure_cpu_plus_elasped_time

@measure_cpu_plus_elasped_time
def setup_udl2_queues(conf):
    queues = {}
    # set up default queues, which is always celery
    queues['default'] = Queue('celery',
                              Exchange(conf['celery_defaults']['CELERY_DEFAULT_EXCHANGE'],
                                       conf['celery_defaults']['CELERY_DEFAULT_EXCHANGE']),
                              routing_key=conf['celery_defaults']['CELERY_DEFAULT_ROUTING_KEY'])
    return queues


@measure_cpu_plus_elasped_time
def setup_celery_conf(udl2_conf, celery, udl_queues):
    celery.conf.update(CELERY_TASK_RESULT_EXPIRES=10,  # TTL for results
        CELERYD_CONCURRENCY=10,  # number of available workers processes
        CELERY_SEND_EVENTS=True,  # send events for monitor
        CELERY_DEFAULT_QUEUE='celery',
        CELERY_DEFAULT_EXCHANGE='direct',
        CELERY_DEFAULT_ROUTING_KEY='celery',
        CELERYD_LOG_DEBUG=udl2_conf['logging']['debug'],
        CELERYD_LOG_LEVEL=udl2_conf['logging']['level'],
        CELERYD_LOG_FILE=udl2_conf['logging']['audit'],
        CELERY_QUEUES=tuple(udl_queues.values()))
    return celery


# import configuration after getting path from environment variable due to celery command don't take extra options
# if UDL2_CONF is not set, use default configurations

try:
    config_path_file = os.environ['UDL2_CONF']
except Exception:
    config_path_file = UDL2_DEFAULT_CONFIG_PATH_FILE

udl2_conf = imp.load_source('udl2_conf', config_path_file)
from udl2_conf import udl2_conf

# the celery instance has to be named as celery due to celery driver looks for this object in celery.py
# this is the default protocol between celery system and our implementation of tasks.

celery = Celery(udl2_conf['celery']['root'],  
                broker=udl2_conf['celery']['broker'], 
                backend=udl2_conf['celery']['backend'], 
                include=udl2_conf['celery']['include'])

# Create all queues entities to be use by task functions

udl2_queues = setup_udl2_queues(udl2_conf)

celery = setup_celery_conf(udl2_conf, celery, udl2_queues)

# configuration options for file splitter
FILE_SPLITTER_CONF = udl2_conf['file_splitter']


if __name__ == '__main__':
    celery.start()
