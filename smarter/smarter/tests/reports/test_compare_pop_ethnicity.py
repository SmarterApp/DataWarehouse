'''
Created on Jul 18, 2013

@author: dip
'''
import unittest
from edcore.tests.utils.unittest_with_edcore_sqlite import Unittest_with_edcore_sqlite,\
    get_unittest_tenant_name
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from pyramid.testing import DummyRequest
from pyramid import testing
from smarter.reports.helpers.constants import Constants
from smarter.reports.compare_pop_report import get_comparing_populations_report,\
    set_default_min_cell_size
from smarter.security.roles.default import DefaultRole  # @UnusedImport
from smarter.reports.helpers import filters
from edauth.tests.test_helper.create_session import create_test_session
from pyramid.security import Allow
import edauth
from edauth.security.user import RoleRelation
from edcore.security.tenant import set_tenant_map


class TestComparingPopulationsEthnicity(Unittest_with_edcore_sqlite):

    def setUp(self):
        cache_opts = {
            'cache.type': 'memory',
            'cache.regions': 'public.data,public.filtered_data,public.shortlived'
        }
        CacheManager(**parse_cache_config_options(cache_opts))

        self.__request = DummyRequest()
        self.__tenant_name = get_unittest_tenant_name()
        set_tenant_map({self.__tenant_name: "NC"})
        # Must set hook_zca to false to work with unittest_with_sqlite.
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        defined_roles = [(Allow, 'PII', ('view', 'logout'))]
        edauth.set_roles(defined_roles)
        # Set up context security
        dummy_session = create_test_session(['PII'])
        dummy_session.set_user_context([RoleRelation("PII", get_unittest_tenant_name(), "NC", "228", None)])
        self.__config.testing_securitypolicy(dummy_session.get_user())
        set_default_min_cell_size(0)

    def tearDown(self):
        # reset the registry
        testing.tearDown()

    def test_comparing_populations_ethnicity_hispanic(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NC'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants.ASMTYEAR] = 2016
        testParam[filters.FILTERS_ETHNICITY] = [filters.FILTERS_ETHNICITY_HISPANIC]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], -1)

    def test_comparing_populations_ethnicity_blk(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NC'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants.ASMTYEAR] = 2016
        testParam[filters.FILTERS_ETHNICITY] = [filters.FILTERS_ETHNICITY_BLACK]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], -1)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], -1)

    def test_comparing_populations_ethnicity_asn(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NC'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants.ASMTYEAR] = 2016
        testParam[filters.FILTERS_ETHNICITY] = [filters.FILTERS_ETHNICITY_ASIAN]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], 0)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], -1)

    def test_comparing_populations_ethnicity_wht(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NC'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants.ASMTYEAR] = 2016
        testParam[filters.FILTERS_ETHNICITY] = [filters.FILTERS_ETHNICITY_WHITE]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], -1)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], -1)

    def test_comparing_populations_ethnicity_ami(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NC'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants.ASMTYEAR] = 2016
        testParam[filters.FILTERS_ETHNICITY] = [filters.FILTERS_ETHNICITY_AMERICAN]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], -1)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], -1)

    def test_comparing_populations_ethnicity_pcf(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NC'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants.ASMTYEAR] = 2016
        testParam[filters.FILTERS_ETHNICITY] = [filters.FILTERS_ETHNICITY_PACIFIC]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], -1)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], -1)

    def test_comparing_populations_ethnicity_two_or_more(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NC'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants.ASMTYEAR] = 2016
        testParam[filters.FILTERS_ETHNICITY] = [filters.FILTERS_ETHNICITY_MULTI]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 0)

    def test_comparing_populations_ethnicity_not_stated(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NC'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants.ASMTYEAR] = 2016
        testParam[filters.FILTERS_ETHNICITY] = [filters.FILTERS_ETHNICITY_NOT_STATED]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 2)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], -1)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], 0)

    def test_comparing_populations_ethnicity_blk_wht(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NC'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants.ASMTYEAR] = 2016
        testParam[filters.FILTERS_ETHNICITY] = [filters.FILTERS_ETHNICITY_ASIAN, filters.FILTERS_ETHNICITY_WHITE]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 1)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], -1)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], -1)

    def test_comparing_populations_ethnicity_all(self):
        testParam = {}
        testParam[Constants.STATECODE] = 'NC'
        testParam[Constants.DISTRICTGUID] = '228'
        testParam[Constants.SCHOOLGUID] = '248'
        testParam[Constants.ASMTYEAR] = 2016
        testParam[filters.FILTERS_ETHNICITY] = [filters.FILTERS_ETHNICITY_AMERICAN,
                                                filters.FILTERS_ETHNICITY_ASIAN,
                                                filters.FILTERS_ETHNICITY_BLACK,
                                                filters.FILTERS_ETHNICITY_HISPANIC,
                                                filters.FILTERS_ETHNICITY_PACIFIC,
                                                filters.FILTERS_ETHNICITY_NOT_STATED,
                                                filters.FILTERS_ETHNICITY_WHITE,
                                                filters.FILTERS_ETHNICITY_MULTI]
        results = get_comparing_populations_report(testParam)
        self.assertEqual(len(results['records']), 2)
        self.assertEqual(results['records'][0]['results']['subject1']['total'], 3)
        self.assertEqual(results['records'][0]['results']['subject2']['total'], -1)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
