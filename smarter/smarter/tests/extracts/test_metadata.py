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
Created on Dec 5, 2013

@author: dip
'''
import unittest

from pyramid.testing import DummyRequest
from pyramid.registry import Registry
from pyramid import testing
from pyramid.security import Allow

from smarter.reports.helpers.constants import Constants
from smarter.extracts.metadata import get_metadata_file_name, get_metadata_file_name_iab, get_asmt_metadata
from edcore.tests.utils.unittest_with_edcore_sqlite import Unittest_with_edcore_sqlite,\
    get_unittest_tenant_name
from edauth.tests.test_helper.create_session import create_test_session
from edauth.security.user import RoleRelation
import edauth
from smarter_common.security.constants import RolesConstants


class TestMetadata(Unittest_with_edcore_sqlite):

    def setUp(self):
        self.reg = Registry()
        self.reg.settings = {'extract.work_zone_base_dir': '/tmp/work_zone',
                             'pickup.gatekeeper.t1': '/t/acb',
                             'pickup.gatekeeper.t2': '/a/df',
                             'pickup.gatekeeper.y': '/a/c',
                             'pickup.sftp.hostname': 'hostname.local.net',
                             'pickup.sftp.user': 'myUser',
                             'pickup.sftp.private_key_file': '/home/users/myUser/.ssh/id_rsa'}
        # Set up user context
        self.__request = DummyRequest()
        # Must set hook_zca to false to work with unittest_with_sqlite
        self.__config = testing.setUp(registry=self.reg, request=self.__request, hook_zca=False)
        defined_roles = [(Allow, RolesConstants.SAR_EXTRACTS, ('view', 'logout'))]
        edauth.set_roles(defined_roles)
        # Set up context security
        dummy_session = create_test_session([RolesConstants.SAR_EXTRACTS])
        dummy_session.set_user_context([RoleRelation(RolesConstants.SAR_EXTRACTS, get_unittest_tenant_name(), "NC", "228", "242")])
        self.__config.testing_securitypolicy(dummy_session)

    def tearDown(self):
        # reset the registry
        testing.tearDown()

    def test_get_metadata_file_name(self):
        params = {Constants.STATECODE: 'UT',
                  Constants.ASMTGUID: 'abc',
                  Constants.ASMTGRADE: '5',
                  Constants.ASMTSUBJECT: 'dd',
                  Constants.ASMTYEAR: '2015',
                  Constants.ASMTTYPE: 'bb'}
        filename = get_metadata_file_name(params)
        self.assertEqual(filename, 'METADATA_ASMT_2015_UT_GRADE_5_DD_BB_abc.json')

    def test_get_metadata_file_name_iab(self):
        params = {Constants.STATECODE: 'UT',
                  Constants.ASMTGUID: 'abc',
                  Constants.ASMTGRADE: '5',
                  Constants.ASMTSUBJECT: 'dd',
                  Constants.ASMTYEAR: '2015',
                  Constants.ASMTTYPE: 'bb',
                  Constants.EFFECTIVE_DATE: '20150111',
                  Constants.ASMT_CLAIM_1_NAME: 'claim @#$ name'}
        filename = get_metadata_file_name_iab(params)
        self.assertEqual(filename, 'METADATA_ASMT_2015_UT_GRADE_5_DD_IAB_claimname_EFF01-11-2015_abc.json')

    def test_get_asmt_metadata_query(self):
        asmt_guid = '20'
        query = get_asmt_metadata('NC', asmt_guid)
        self.assertIsNotNone(query)
        self.assertIn('dim_asmt.asmt_guid', str(query._whereclause))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
