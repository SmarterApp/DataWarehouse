'''
Created on Mar 17, 2014

@author: tosako
'''
from edmigrate.settings.config import Config, setup_settings, get_setting
from edworker.celery import get_config_file
import configparser
from edmigrate.database.repmgr_connector import RepMgrDBConnection
from edmigrate.utils.constants import Constants
from sqlalchemy.sql.expression import select
import re
from edmigrate.exceptions import NoMasterFoundException, NoNodeIDFoundException


def read_ini(file):
    config = configparser.ConfigParser()
    config.read(file)
    return config['app:main']


def get_broker_url(config=None):
    if config is None:
        config_file = get_config_file()
        if config_file is None:
            config = configparser.ConfigParser()
            config['app:mian'] = {}
        else:
            config = read_ini(config_file)

    url = "memory://"

    try:
        celery_always_eager = config.getboolean(Config.EAGER_MODE, False)
    except:
        celery_always_eager = False

    if not celery_always_eager:
        try:
            url = config.get(Config.BROKER_URL, url)
        except:
            pass
    return url


def get_my_master_by_id(my_node_id):
    master_hostname = None
    with RepMgrDBConnection() as conn:
        repl_nodes = conn.get_table(Constants.REPL_NODES)
        repl_status = conn.get_table(Constants.REPL_STATUS)
        query = select([repl_nodes.c.conninfo.label('name')],
                       from_obj=[repl_nodes
                                 .join(repl_status, repl_status.c.primary_node == repl_nodes.c.id)])\
            .where(repl_status.c.standby_node == my_node_id)
        results = conn.get_result(query)
        if results:
            result = results[0]
            node_name = result['name']
            m = re.match('^host=(\S+)\s+', node_name)
            if m:
                master_hostname = m.group(1)
    if not master_hostname:
        raise NoMasterFoundException()
    return master_hostname


def get_node_id_from_hostname(hostname):
    '''
    look up repl_nodes for node_id of the host.
    '''
    node_id = None
    with RepMgrDBConnection() as conn:
        repl_nodes = conn.get_table(Constants.REPL_NODES)
        query = select([repl_nodes.c.id.label('id')],
                       repl_nodes.c.name.like("%" + hostname + "%"),
                       from_obj=[repl_nodes])
        results = conn.get_result(query)
        if results:
            result = results[0]
            node_id = result['id']
    if not node_id:
        raise NoNodeIDFoundException()
    return node_id


class Singleton(type):
    _instances = {}

    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]
