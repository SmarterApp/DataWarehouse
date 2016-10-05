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
This module uses the Beaker library to store user sessions in
backend storage (database, memcached, or other)

Beaker config parameters are set in an .ini file.

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
    def create_new_session(self, session, overwrite_timeout=False):
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
        self.cache_mgr = CacheManager(**parse_cache_config_options(settings))
        self.batch_timeout = int(settings.get('batch.user.session.timeout'))
        logger.info('TEST SESSION: __init__ , batch.user.session.timeout :' + settings.get('batch.user.session.timeout'))

    def create_new_session(self, session, overwrite_timeout=False):
        '''
        Creates a new session
        '''
        self.update_session(session, overwrite_timeout=overwrite_timeout)

    def update_session(self, session, overwrite_timeout=False):
        '''
        Given a session, persist it
        '''
        _id = session.get_session_id()
        region = self.__get_cache_region(_id)
        # Overwrite the timeout for batch user sessions
        if overwrite_timeout:
            region.expiretime = self.batch_timeout
        region.put(_id, session)
        message = "TEST SESSION: update_session, session: {0}".format(str(_id))
        logger.info(message)

    def get_session(self, session_id):
        '''
        Return session from persistent storage
        '''
        region = self.__get_cache_region(session_id)
        if session_id not in region:
            logger.info('Session is not found in cache. It may have expired or connection to memcached is down')
            message = "TEST SESSION: Session is not found in cache, session: {0}".format(str(session_id))
            logger.info(message)
            return None
        return region.get(session_id)

    def delete_session(self, session_id):
        '''
        Delete session from persistent storage
        '''
        # delete from db doesn't work
        logger.info('TEST: delete_session, session_id' + session_id)
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
        logger.info('TEST SESSION: clear')
