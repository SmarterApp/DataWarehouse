# (c) 2014 The Regents of the University of California. All rights reserved,
# subject to the license below.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0. Unless required by
# applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

'''
Created on Aug 5, 2013

@author: dawu
'''
import unittest
from edcore.tests.utils.unittest_with_edcore_sqlite import Unittest_with_edcore_sqlite,\
    get_unittest_tenant_name
from edapi.tests.dummy import DummyRequest
from pyramid import testing
from smarter.reports.helpers.aggregate_dim import get_aggregate_dim_cache_route, get_aggregate_dim_cache_route_cache_key,\
    get_aggregate_dim_interim
from beaker.util import parse_cache_config_options
from beaker.cache import CacheManager
from edauth.tests.test_helper.create_session import create_test_session
from smarter.reports.helpers.constants import AssessmentType
from smarter.reports.helpers.constants import Constants


class TestCustomMetaData(Unittest_with_edcore_sqlite):

    def setUp(self):
        cache_opts = {
            'cache.type': 'memory',
            'cache.regions': 'public.shortlived'
        }
        CacheManager(**parse_cache_config_options(cache_opts))

        self.__request = DummyRequest()
        # Must set hook_zca to false to work with unittest_with_sqlite
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        dummy_session = create_test_session(['TEACHER'], uid='272')
        self.__config.testing_securitypolicy(dummy_session)

    def tearDown(self):
        # reset the registry
        testing.tearDown()

    def test_get_aggregate_dim(self):
        tenant = get_unittest_tenant_name()
        agg_results = get_aggregate_dim_interim('NC', None, None, 2016, tenant, {'subject1': 'Math', 'subject2': 'ELA'})
        records = agg_results[Constants.RECORDS]
        self.assertEqual(4, len(records))
        record = records[3]
        results = record[Constants.RESULTS]
        self.assertFalse(results['subject1'][Constants.HASINTERIM])
        self.assertTrue(results['subject2'][Constants.HASINTERIM])

    def test_get_aggregate_dim_cache_route(self):
        self.assertIsNone(get_aggregate_dim_cache_route('NC', 'district', 'school', None, None, None, None))
        self.assertEqual('public.shortlived', get_aggregate_dim_cache_route('NC', 'district', None, None, None, None, None))
        self.assertEqual('public.shortlived', get_aggregate_dim_cache_route('NC', None, None, None, None, None, None))

    def test_get_aggregate_dim_cache_route_cache_key(self):
        key = get_aggregate_dim_cache_route_cache_key('NC', 'district', None, 'asmtYear', 'tenant', 'subject_key', 'subject', False)
        self.assertEqual(key[0], 'NC')
        self.assertEqual(key[1], 'district')
        self.assertEqual(key[2], 'asmtYear')
        self.assertEqual(key[3], 'subject')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
