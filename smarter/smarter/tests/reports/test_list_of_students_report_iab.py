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
Created on Oct 21, 2014

@author: tosako
'''
import unittest
from pyramid.testing import DummyRequest
from pyramid import testing
from pyramid.security import Allow
from edcore.tests.utils.unittest_with_edcore_sqlite import Unittest_with_edcore_sqlite, get_unittest_tenant_name
from edauth.tests.test_helper.create_session import create_test_session
import edauth
from smarter.reports.helpers.metadata import get_subjects_map
from smarter.reports.helpers.filters import dmg_map
from smarter_common.security.constants import RolesConstants
from edcore.security.tenant import set_tenant_map
from smarter.security.roles.default import DefaultRole  # @UnusedImport
from smarter.security.roles.pii import PII  # @UnusedImport
from smarter.reports.helpers.constants import Constants, AssessmentType
from smarter.reports.list_of_students_report_iab import get_list_of_students_iab, \
    get_list_of_students_report_iab, format_assessments_iab
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from unittest.mock import patch


class Test(Unittest_with_edcore_sqlite):

    def setUp(self):
        cache_opts = {
            'cache.type': 'memory',
            'cache.regions': 'public.data,public.filtered_data,public.shortlived,public.very_shortlived'
        }

        CacheManager(**parse_cache_config_options(cache_opts))
        # Set up user context
        self.__request = DummyRequest()
        # Must set hook_zca to false to work with unittest_with_sqlite
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        defined_roles = [(Allow, RolesConstants.PII, ('view', 'logout'))]
        edauth.set_roles(defined_roles)
        set_tenant_map({get_unittest_tenant_name(): 'NC'})
        # Set up context security
        dummy_session = create_test_session([RolesConstants.PII])
        self.__config.testing_securitypolicy(dummy_session.get_user())

    def test_get_list_of_students_for_iab(self):
        params = {}
        params[Constants.STATECODE] = 'NC'
        params[Constants.DISTRICTGUID] = '229'
        params[Constants.SCHOOLGUID] = '936'
        params[Constants.ASMTGRADE] = '03'
        params[Constants.ASMTSUBJECT] = ['Math']
        params[Constants.ASMTYEAR] = 2015
        results = get_list_of_students_iab(params)
        self.assertEqual(6, len(results))

    def test_get_list_of_students_report_iab(self):
        params = {}
        params[Constants.STATECODE] = 'NC'
        params[Constants.DISTRICTGUID] = '229'
        params[Constants.SCHOOLGUID] = '936'
        params[Constants.ASMTGRADE] = '03'
        params[Constants.ASMTSUBJECT] = ['Math']
        params[Constants.ASMTYEAR] = 2015
        los_results = get_list_of_students_report_iab(params)
        data = los_results['assessments'][AssessmentType.INTERIM_ASSESSMENT_BLOCKS]['34b99412-fd5b-48f0-8ce8-f8ca3788634a']
        subject1 = data['subject1']
        claim = subject1['Fractions']
        self.assertEqual(5, len(subject1))
        self.assertEqual(1, len(claim))

    @patch('smarter.reports.list_of_students_report_iab.get_student_demographic')
    @patch('smarter.reports.list_of_students_report_iab.get_claims')
    def test_format_assessments_iab(self, mock_get_claims, mock_get_student_demographic):
        mock_get_claims.return_value = [{'name': 'claim'}]
        result = dmg_map.copy()
        result['first_name'] = 'Johnny'
        result['middle_name'] = 'Drake'
        result['last_name'] = 'Darko'
        result['student_id'] = '923436'
        result['date_taken'] = '20140301'
        result['enrollment_grade'] = '3'
        result['state_code'] = 'NC'
        result[Constants.ROWID] = 2015
        result['complete'] = True
        result['administration_condition'] = "IN"
        result['asmt_grade'] = "A"
        result['asmt_subject'] = "Math"
        results = [result]
        subjects_map = {'Math': 'Math'}
        assessments = format_assessments_iab(results, subjects_map)
        assessmentObject = assessments[AssessmentType.INTERIM_ASSESSMENT_BLOCKS][result['student_id']][result['asmt_subject']]
        self.assertEqual(assessmentObject['claim'][0]['complete'], result['complete'])
        self.assertEqual(assessmentObject['claim'][0]['administration_condition'], result['administration_condition'])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
