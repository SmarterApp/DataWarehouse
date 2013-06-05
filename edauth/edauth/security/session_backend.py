'''
Created on May 24, 2013

@author: dip
'''
import logging
from zope.interface import interface
from zope.interface.declarations import implementer
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from zope import component


logger = logging.getLogger('edauth')


def get_session_backend():
    '''
    Returns the current instance of backend storage for sessions
    '''
    return component.getUtility(ISessionBackend).get_backend()


class ISessionBackend(interface.Interface):
    '''
    Interface to session backend
    '''
    def get_backend(self):
        pass


@implementer(ISessionBackend)
class SessionBackend():
    '''
    Keeps track of instance of backend used to store sessions
    '''
    def __init__(self, settings):
        self.backend = BeakerBackend(settings)

    def get_backend(self):
        return self.backend


class Backend(object):
    '''
    Interface for backend used to store sessions
    '''
    def create_new_session(self, session):
        pass

    def update_session(self, session):
        pass

    def get_session(self, session_id):
        pass

    def delete_session(self, session_id):
        pass

    def clear(self):
        pass


class BeakerBackend(Backend):
    '''
    Manipulates session that resides in persistent storage (memory, memcached)
    '''
    def __init__(self, settings):
        # We'll save both the cachemanager
        self.cache_mgr = CacheManager(**parse_cache_config_options(settings))

    def create_new_session(self, session):
        '''
        Creates a new session
        '''
        self.update_session(session)

    def update_session(self, session):
        '''
        Given a session, persist it
        '''
        _id = session.get_session_id()
        region = self.__get_cache_region(_id)
        region.put(_id, session)

    def get_session(self, session_id):
        '''
        Return session from persistent storage
        '''
        region = self.__get_cache_region(session_id)
        if not session_id in region:
            logger.info('Session is not found in cache. It may have expired or connection to memcached is down')
            return None
        return region.get(session_id)

    def delete_session(self, session_id):
        '''
        Delete session from persistent storage
        '''
        # delete from db doesn't work
        region = self.__get_cache_region(session_id)
        if session_id in region:
            # works for memcached
            region.remove_value(session_id)

    def __get_cache_region(self, key):
        return self.cache_mgr.get_cache_region('edware_session_' + key, 'session')

    def clear(self):
        '''
        clear cache
        '''
        self.cache_region.clear()
