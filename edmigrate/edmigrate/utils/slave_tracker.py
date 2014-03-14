'''
Created on Mar 14, 2014

@author: tosako
'''
import threading
from edmigrate.utils.constants import Constants
import time


class Singleton(type):
    _instances = {}
    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]

class SlaveTrackerException(Exception):
    def __init__(self, msg='SlaveTrackerException'):
        self.__msg = msg
    def __str__(self):
        return repr(self.__msg)

class SlaveAlreadyRegisteredException(SlaveTrackerException):
    def __init__(self, node_id):
        SlaveTrackerException.__init__(self, msg='Slave [' + node_id + '] has already registered')

class SlaveNotRegisteredException(SlaveTrackerException):
    def __init__(self, node_id):
        SlaveTrackerException.__init__(self, msg='Slave [' + node_id + '] was not registered')

class SlaveStatusTimedoutException(SlaveTrackerException):
    def __init__(self, node_id, timeout):
        SlaveTrackerException.__init__(self, msg='Timedout after ' + timeout + ' seconds. Slave [' + node_id + '] was not registered')

class SlaveTracker(metaclass=Singleton):
    __lock = threading.Lock()

    def __init__(self):
        self.__lock.acquire()
        self.__slaves = {}
        self.__lock.release()

    def add_slave(self, node_id):
        self.__lock.acquire()
        if node_id in self.__slaves:
            self.__lock.release()
            raise SlaveAlreadyRegisteredException(node_id)
        node = {}
        node[Constants.SLAVE_GROUP] = None
        node[Constants.SLAVE_PGPOOL_CONNECTION_STATUS] = Constants.SLAVE_CONNECTION_STATUS_CONNECTED
        node[Constants.SLAVE_MASTER_CONNECTION_STATUS] = Constants.SLAVE_CONNECTION_STATUS_CONNECTED
        self.__slaves[node_id] = node
        self.__lock.release()

    def set_pgpool_connected(self, node_id):
        self._set_slave_status(node_id, Constants.SLAVE_PGPOOL_CONNECTION_STATUS, Constants.SLAVE_CONNECTION_STATUS_CONNECTED)

    def set_pgpool_disconnected(self, node_id):
        self._set_slave_status(node_id, Constants.SLAVE_PGPOOL_CONNECTION_STATUS, Constants.SLAVE_CONNECTION_STATUS_DISCONNECTED)

    def set_master_connected(self, node_id):
        self._set_slave_status(node_id, Constants.SLAVE_MASTER_CONNECTION_STATUS, Constants.SLAVE_CONNECTION_STATUS_CONNECTED)

    def set_master_disconnected(self, node_id):
        self._set_slave_status(node_id, Constants.SLAVE_MASTER_CONNECTION_STATUS, Constants.SLAVE_CONNECTION_STATUS_DISCONNECTED)

    def set_slave_group(self, node_id, group_name):
        self._set_slave_status(node_id, Constants.SLAVE_GROUP, group_name)

    def is_pgpool_connected(self, node_id, timeout=5):
        return self._is_slave_status(node_id, Constants.SLAVE_PGPOOL_CONNECTION_STATUS, Constants.SLAVE_CONNECTION_STATUS_CONNECTED, timeout=timeout)

    def is_pgpool_disconnected(self, node_id, timeout=5):
        return self._is_slave_status(node_id, Constants.SLAVE_PGPOOL_CONNECTION_STATUS, Constants.SLAVE_CONNECTION_STATUS_DISCONNECTED, timeout=timeout)

    def is_master_connected(self, node_id, timeout=5):
        return self._is_slave_status(node_id, Constants.SLAVE_MASTER_CONNECTION_STATUS, Constants.SLAVE_CONNECTION_STATUS_CONNECTED, timeout=timeout)

    def is_master_disconnected(self, node_id, timeout=5):
        return self._is_slave_status(node_id, Constants.SLAVE_MASTER_CONNECTION_STATUS, Constants.SLAVE_CONNECTION_STATUS_DISCONNECTED, timeout=timeout)

    def get_slave_ids(self):
        self.__lock.acquire()
        ids = self.__slaves.keys()
        self.__lock.release()
        return ids.sort()

    def reset(self):
        self.__lock.acquire()
        self.__slaves.clear()
        self.__lock.release()

    def _set_slave_status(self, node_id, name, status):
        self.__lock.acquire()
        node = self.__slaves.get(node_id)
        if not node:
            self.__lock.release()
            raise SlaveNotRegisteredException(node_id)
        node[name] = status
        self.__lock.release()

    def _is_slave_status(self, node_id, name, expected_value, timeout=5):
        start_time = time.time()
        while True:
            self.__lock.acquire()
            node = self.__slaves.get(node_id)
            self.__lock.release()
            if not node:
                current_time = time.time()
                if current_time - start_time > timeout:
                    raise SlaveStatusTimedoutException(node_id, timeout)
                time.sleep(1)
            else:
                break
        return node[name] == expected_value
