'''
Created on May 24, 2013

@author: dip
'''
import unittest
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from edauth.security.session import Session
from edauth.security.session_backend import BeakerBackend


class TestBeakerBackend(unittest.TestCase):

    def setUp(self):
        reg = {}
        reg['cache.expire'] = 10
        reg['cache.regions'] = 'session'
        reg['cache.type'] = 'memory'
        self.cachemgr = CacheManager(**parse_cache_config_options(reg))
        self.backend = BeakerBackend(reg)

    def __get_region(self, key):
        return self.cachemgr.get_cache_region('edware_session_' + key, 'session')

    def test_create_new_session(self):
        session = Session()
        session.set_session_id('123')
        self.backend.create_new_session(session)
        self.assertIsNotNone(self.__get_region('123').get('123'))

    def test_get_session_from_persistence_with_existing_session(self):
        session = Session()
        session.set_session_id('456')
        session.set_uid('abc')
        self.backend.create_new_session(session)
        lookup = self.backend.get_session('456')
        self.assertEqual(lookup.get_uid(), 'abc')

    def test_get_session_invalid_session(self):
        lookup = self.backend.get_session('idontexist')
        self.assertIsNone(lookup)

    def test_delete_session(self):
        session = Session()
        session.set_session_id('456')
        session.set_uid('abc')
        self.backend.create_new_session(session)
        self.backend.delete_session('456')
        self.assertFalse('456' in self.__get_region('456'))

    def test_update_session(self):
        session = Session()
        session.set_session_id('456')
        session.set_uid('abc')
        self.backend.create_new_session(session)
        session.set_uid('def')
        self.backend.update_session(session)
        lookup = self.__get_region('456').get('456')
        self.assertEquals(lookup.get_uid(), 'def')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
