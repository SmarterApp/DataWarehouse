'''
Created on May 9, 2013

@author: dip
'''
import unittest

from sqlalchemy.sql.expression import select
from pyramid.security import Allow
from pyramid.testing import DummyRequest
from pyramid import testing

from edcore.tests.utils.unittest_with_edcore_sqlite import Unittest_with_edcore_sqlite,\
    UnittestEdcoreDBConnection, get_unittest_tenant_name
from smarter.reports.helpers.constants import Constants
from smarter.security.roles.state_level import StateLevel
from smarter_common.security.constants import RolesConstants
import edauth
from edcore.security.tenant import set_tenant_map
from edauth.tests.test_helper.create_session import create_test_session
from edauth.security.user import RoleRelation


class TestStateLevelContextSecurity(Unittest_with_edcore_sqlite):

    def setUp(self):
        defined_roles = [(Allow, RolesConstants.SRS_EXTRACTS, ('view', 'logout')),
                         (Allow, RolesConstants.SRC_EXTRACTS, ('view', 'logout'))]
        self.role_constants = [RolesConstants.SRS_EXTRACTS, RolesConstants.SRC_EXTRACTS]
        edauth.set_roles(defined_roles)
        self.tenant = get_unittest_tenant_name()
        set_tenant_map({self.tenant: 'ES'})
        dummy_session = create_test_session([RolesConstants.SRS_EXTRACTS, RolesConstants.SRC_EXTRACTS])
        dummy_session.set_user_context([RoleRelation(RolesConstants.SRS_EXTRACTS, self.tenant, None, None, None),
                                        RoleRelation(RolesConstants.SRC_EXTRACTS, self.tenant, None, None, None)])
        self.user = dummy_session.get_user()
        self.__request = DummyRequest()
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        self.__config.testing_securitypolicy(self.user)

    def verify_has_context_with_context(self, role):
        with UnittestEdcoreDBConnection() as connection:
            state_level = StateLevel(connection, role)
            context = state_level.check_context(self.tenant, self.user, ['115f7b10-9e18-11e2-9e96-0800200c9a66'])
            self.assertTrue(context)

    def verify_has_context_with_no_context(self, role):
        with UnittestEdcoreDBConnection() as connection:
            state_level = StateLevel(connection, role)
            context = state_level.check_context(self.tenant, self.user, ['notyourstudent'])
            self.assertFalse(context)

    def verify_has_context_with_some_invalid_guids(self, role):
        with UnittestEdcoreDBConnection() as connection:
            state_level = StateLevel(connection, role)
            context = state_level.check_context(self.tenant, self.user, ['115f7b10-9e18-11e2-9e96-0800200c9a66', 'notyourstudent'])
            self.assertFalse(context)

    def test_add_context_without_tenant(self):
        dummy_session = create_test_session([RolesConstants.SRS_EXTRACTS, RolesConstants.SRC_EXTRACTS])
        dummy_session.set_user_context([RoleRelation(RolesConstants.SRS_EXTRACTS, None, None, None, None),
                                        RoleRelation(RolesConstants.SRC_EXTRACTS, None, None, None, None)])
        self.user = dummy_session.get_user()
        self.__request = DummyRequest()
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        self.__config.testing_securitypolicy(self.user)

        with UnittestEdcoreDBConnection() as connection:
            dim_student = connection.get_table(Constants.DIM_STUDENT)
            query = select([dim_student.c.student_id], from_obj=[dim_student])
            state_level = StateLevel(connection, RolesConstants.SRS_EXTRACTS)
            query = state_level.add_context(self.tenant, self.user, query)
            self.assertIsNone(query._whereclause)

    def test_add_context_with_tenant(self):
        dummy_session = create_test_session([RolesConstants.SRS_EXTRACTS, RolesConstants.SRC_EXTRACTS])
        dummy_session.set_user_context([RoleRelation(RolesConstants.SRS_EXTRACTS, self.tenant, None, None, None),
                                        RoleRelation(RolesConstants.SRC_EXTRACTS, self.tenant, None, None, None)])
        self.user = dummy_session.get_user()
        self.__request = DummyRequest()
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        self.__config.testing_securitypolicy(self.user)

        with UnittestEdcoreDBConnection() as connection:
            dim_student = connection.get_table(Constants.DIM_STUDENT)
            query = select([dim_student.c.student_id], from_obj=[dim_student])
            state_level = StateLevel(connection, RolesConstants.SRS_EXTRACTS)
            query = state_level.add_context(get_unittest_tenant_name(), self.user, query)
            self.assertIsNone(query._whereclause)

    def test_add_context_with_state_level(self):
        dummy_session = create_test_session([RolesConstants.SRS_EXTRACTS, RolesConstants.SRC_EXTRACTS])
        dummy_session.set_user_context([RoleRelation(RolesConstants.SRS_EXTRACTS, self.tenant, 'ZZ', None, None),
                                        RoleRelation(RolesConstants.SRC_EXTRACTS, self.tenant, 'ZZ', None, None)])
        self.user = dummy_session.get_user()
        self.__request = DummyRequest()
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        self.__config.testing_securitypolicy(self.user)
        # Checks that the query has applied where clause
        with UnittestEdcoreDBConnection() as connection:
            fact = connection.get_table(Constants.FACT_ASMT_OUTCOME_VW)
            query = select([fact.c.student_id], from_obj=[fact])
            state_level = StateLevel(connection, RolesConstants.SRS_EXTRACTS)
            query = state_level.add_context(get_unittest_tenant_name(), self.user, query)
            self.assertIsNotNone(query._whereclause)
            result = connection.get_result(query)
            self.assertEqual(len(result), 0)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
