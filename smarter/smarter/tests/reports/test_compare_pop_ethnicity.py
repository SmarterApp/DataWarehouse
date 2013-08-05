'''
Created on Jul 18, 2013

@author: dip
'''
import unittest
from smarter.tests.utils.unittest_with_smarter_sqlite import Unittest_with_smarter_sqlite,\
    UnittestSmarterDBConnection, get_unittest_tenant_name
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from pyramid.testing import DummyRequest
from pyramid import testing
from edauth.security.session import Session
from smarter.reports.helpers.constants import Constants
from smarter.reports.filters import Constants_filter_names
from smarter.reports.compare_pop_report import get_comparing_populations_report
from smarter.security.roles.default import DefaultRole  # @UnusedImport


class TestComparingPopulationsEthnicity(Unittest_with_smarter_sqlite):

    def setUp(self):
        cache_opts = {
            'cache.type': 'memory',
            'cache.regions': 'public.data,public.filtered_data,public.shortlived'
        }
        CacheManager(**parse_cache_config_options(cache_opts))

        self.__request = DummyRequest()
        # Must set hook_zca to false to work with unittest_with_sqlite.
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        with UnittestSmarterDBConnection() as connection:
            # Insert into user_mapping table
            user_mapping = connection.get_table('user_mapping')
            connection.execute(user_mapping.insert(), user_id='272', guid='272')
        dummy_session = Session()
        dummy_session.set_session_id('123')
        dummy_session.set_roles(['STATE_EDUCATION_ADMINISTRATOR_1'])
        dummy_session.set_uid('272')
        dummy_session.set_tenant(get_unittest_tenant_name())
        self.__config.testing_securitypolicy(dummy_session)

    def tearDown(self):
        # reset the registry
        testing.tearDown()

        # delete user_mapping entries
        with UnittestSmarterDBConnection() as connection:
            user_mapping = connection.get_table('user_mapping')
            connection.execute(user_mapping.delete())

    def test_comparing_populations_ethnicity_hispanic(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NY'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants_filter_names.ETHNICITY] = [Constants_filter_names.DEMOGRAPHICS_ETHNICITY_HISPANIC]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], 3)

    def test_comparing_populations_ethnicity_blk(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NY'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants_filter_names.ETHNICITY] = [Constants_filter_names.DEMOGRAPHICS_ETHNICITY_BLACK]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], 1)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], 1)

    def test_comparing_populations_ethnicity_asn(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NY'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants_filter_names.ETHNICITY] = [Constants_filter_names.DEMOGRAPHICS_ETHNICITY_ASIAN]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], 1)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], 1)

    def test_comparing_populations_ethnicity_wht(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NY'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants_filter_names.ETHNICITY] = [Constants_filter_names.DEMOGRAPHICS_ETHNICITY_WHITE]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], 1)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], 1)

    def test_comparing_populations_ethnicity_ami(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NY'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants_filter_names.ETHNICITY] = [Constants_filter_names.DEMOGRAPHICS_ETHNICITY_AMERICAN]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], 1)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], 1)

    def test_comparing_populations_ethnicity_pcf(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NY'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants_filter_names.ETHNICITY] = [Constants_filter_names.DEMOGRAPHICS_ETHNICITY_PACIFIC]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], 1)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], 1)

    def test_comparing_populations_ethnicity_two_or_more(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NY'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants_filter_names.ETHNICITY] = [Constants_filter_names.DEMOGRAPHICS_ETHNICITY_MULTI]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], 1)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], 1)

    def test_comparing_populations_ethnicity_not_stated(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NY'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants_filter_names.ETHNICITY] = [Constants_filter_names.NOT_STATED]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], 2)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], 2)

    def test_comparing_populations_ethnicity_blk_wht(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NY'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants_filter_names.ETHNICITY] = [Constants_filter_names.DEMOGRAPHICS_ETHNICITY_ASIAN, Constants_filter_names.DEMOGRAPHICS_ETHNICITY_WHITE]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], 2)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], 2)

    def test_comparing_populations_ethnicity_all(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NY'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants_filter_names.ETHNICITY] = [Constants_filter_names.DEMOGRAPHICS_ETHNICITY_AMERICAN,
                                                       Constants_filter_names.DEMOGRAPHICS_ETHNICITY_ASIAN,
                                                       Constants_filter_names.DEMOGRAPHICS_ETHNICITY_BLACK,
                                                       Constants_filter_names.DEMOGRAPHICS_ETHNICITY_HISPANIC,
                                                       Constants_filter_names.DEMOGRAPHICS_ETHNICITY_PACIFIC,
                                                       Constants_filter_names.NOT_STATED,
                                                       Constants_filter_names.DEMOGRAPHICS_ETHNICITY_WHITE,
                                                       Constants_filter_names.DEMOGRAPHICS_ETHNICITY_MULTI]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], 11)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], 11)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
