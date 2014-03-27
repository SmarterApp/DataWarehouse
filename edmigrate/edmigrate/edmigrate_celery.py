__author__ = 'sravi'
from edcore.database.stats_connector import StatsDBConnection
from edworker.celery import setup_celery as setup_for_worker, configure_celeryd, get_config_file,\
    setup_celery_for_caller as worker_setup_celery_for_caller
from edmigrate.settings.config import setup_settings
import logging
import logging.config
from edcore.database import initialize_db
from edmigrate.database.repmgr_connector import RepMgrDBConnection
from edmigrate.utils.constants import Constants


logger = logging.getLogger(Constants.WORKER_NAME)
PREFIX = 'migrate.celery'


def setup_celery_for_caller(settings, prefix=PREFIX):
    worker_setup_celery_for_caller(celery, settings, prefix)
    setup_settings(settings)


def setup_celery(settings, prefix=PREFIX):
    '''
    Setup celery based on parameters defined in setting (ini file).
    This calls by client application when dictionary of settings is given

    :param settings:  dict of configurations
    :param prefix: prefix in configurations used for configuring celery
    '''
    setup_for_worker(celery, settings, prefix)
    setup_settings(settings)


# Create an instance of celery, check if it's for prod celeryd mode and configure it for prod mode if so
celery, conf = configure_celeryd(PREFIX, prefix=PREFIX)
prod_config = get_config_file()
if prod_config:
    # We should only need to setup db connection in prod mode
    #setup_db_connection(conf)
    initialize_db(RepMgrDBConnection, conf)
    initialize_db(StatsDBConnection, conf)
    setup_settings(conf)
    logging.config.fileConfig(prod_config)
