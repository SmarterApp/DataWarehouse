'''
Created on May 9, 2013

@author: dip
'''
import unittest

from sqlalchemy.sql.expression import select, or_
from pyramid import testing
from pyramid.testing import DummyRequest
from pyramid.security import Allow

from edcore.tests.utils.unittest_with_edcore_sqlite import Unittest_with_edcore_sqlite,\
    UnittestEdcoreDBConnection, get_unittest_tenant_name
from smarter.reports.helpers.constants import Constants
from smarter.security.roles.pii import PII
from edauth.tests.test_helper.create_session import create_test_session
from edauth.security.user import RoleRelation
from edcore.security.tenant import set_tenant_map
import edauth
from smarter_common.security.constants import RolesConstants


class TestPIIContextSecurity(Unittest_with_edcore_sqlite):

    def setUp(self):
        defined_roles = [(Allow, RolesConstants.PII, ('view', 'logout')),
                         (Allow, RolesConstants.SAR_EXTRACTS, ('view', 'logout'))]
        edauth.set_roles(defined_roles)
        self.tenant = get_unittest_tenant_name()
        set_tenant_map({self.tenant: "NC"})
        dummy_session = create_test_session([RolesConstants.PII])
        dummy_session.set_user_context([RoleRelation(RolesConstants.PII, get_unittest_tenant_name(), "NC", "228", "242"),
                                        RoleRelation(RolesConstants.SAR_EXTRACTS, get_unittest_tenant_name(), "NC", "228", "242")])
        self.user = dummy_session.get_user()
        self.__request = DummyRequest()
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        self.__config.testing_securitypolicy(self.user)

    def test_check_context_with_context(self):
        with UnittestEdcoreDBConnection() as connection:
            pii = PII(connection, RolesConstants.PII)
            student_ids = ['e2f3c6a5-e28b-43e8-817b-fc7afed02b9b']

            context = pii.check_context(self.tenant, self.user, student_ids)
            self.assertTrue(context)

    def test_check_context_with_no_context(self):
        with UnittestEdcoreDBConnection() as connection:
            pii = PII(connection, RolesConstants.PII)
            student_ids = ['dd']

            context = pii.check_context(self.tenant, self.user, student_ids)
            self.assertFalse(context)

    def test_check_context_with_no_context_to_all_guids(self):
        with UnittestEdcoreDBConnection() as connection:
            pii = PII(connection, RolesConstants.PII)
            student_ids = ['dd', 'e2f3c6a5-e28b-43e8-817b-fc7afed02b9b']

            context = pii.check_context(self.tenant, self.user, student_ids)
            self.assertFalse(context)

    def test_check_context_with_empty_context(self):
        with UnittestEdcoreDBConnection() as connection:
            pii = PII(connection, RolesConstants.PII)
            student_ids = []

            context = pii.check_context(self.tenant, self.user, student_ids)
            self.assertTrue(context)

    def test_add_context_without_tenant(self):
        dummy_session = create_test_session([RolesConstants.PII])
        dummy_session.set_user_context([RoleRelation(RolesConstants.PII, None, None, None, None)])
        self.user = dummy_session.get_user()
        self.__request = DummyRequest()
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        self.__config.testing_securitypolicy(self.user)

        with UnittestEdcoreDBConnection() as connection:
            fact = connection.get_table(Constants.FACT_ASMT_OUTCOME_VW)
            query = select([fact.c.state_code], from_obj=[fact])
            pii = PII(connection, RolesConstants.PII)
            query = pii.add_context(self.tenant, self.user, query)
            result = connection.get_result(query)
            self.assertEqual(1228, len(result))

    def test_add_context_with_tenant(self):
        dummy_session = create_test_session([RolesConstants.PII])
        dummy_session.set_user_context([RoleRelation(RolesConstants.PII, self.tenant, None, None, None)])
        self.user = dummy_session.get_user()
        self.__request = DummyRequest()
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        self.__config.testing_securitypolicy(self.user)

        with UnittestEdcoreDBConnection() as connection:
            fact = connection.get_table(Constants.FACT_ASMT_OUTCOME_VW)
            query = select([fact.c.state_code], from_obj=[fact])
            pii = PII(connection, RolesConstants.PII)
            query = pii.add_context(get_unittest_tenant_name(), self.user, query)
            result = connection.get_result(query)
            self.assertEqual(1228, len(result))

    def test_add_context_with_state_level(self):
        dummy_session = create_test_session([RolesConstants.PII])
        dummy_session.set_user_context([RoleRelation(RolesConstants.PII, self.tenant, 'NC', None, None)])
        self.user = dummy_session.get_user()
        self.__request = DummyRequest()
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        self.__config.testing_securitypolicy(self.user)
        # Checks that the query has applied where clause
        with UnittestEdcoreDBConnection() as connection:
            fact = connection.get_table(Constants.FACT_ASMT_OUTCOME_VW)
            query = select([fact.c.student_id], from_obj=[fact])
            pii = PII(connection, RolesConstants.PII)
            query = pii.add_context(get_unittest_tenant_name(), self.user, query)
            self.assertIsNotNone(query._whereclause)
            result = connection.get_result(query)
            self.assertEqual(len(result), 1228)

    def test_add_context_with_district_level(self):
        dummy_session = create_test_session([RolesConstants.PII])
        dummy_session.set_user_context([RoleRelation(RolesConstants.PII, self.tenant, 'NC', '228', None)])
        self.user = dummy_session.get_user()
        self.__request = DummyRequest()
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        self.__config.testing_securitypolicy(self.user)
        # Checks that the query has applied where clause
        with UnittestEdcoreDBConnection() as connection:
            fact = connection.get_table(Constants.FACT_ASMT_OUTCOME_VW)
            query = select([fact.c.state_code], from_obj=[fact])
            pii = PII(connection, RolesConstants.PII)
            query = pii.add_context(get_unittest_tenant_name(), self.user, query)
            result = connection.get_result(query)
            self.assertEqual(344, len(result))

    def test_add_context_with_school_level(self):
        dummy_session = create_test_session([RolesConstants.PII])
        dummy_session.set_user_context([RoleRelation(RolesConstants.PII, self.tenant, 'NC', '228', '242')])
        self.user = dummy_session.get_user()
        self.__request = DummyRequest()
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        self.__config.testing_securitypolicy(self.user)
        # Checks that the query has applied where clause
        with UnittestEdcoreDBConnection() as connection:
            fact = connection.get_table(Constants.FACT_ASMT_OUTCOME_VW)
            query = select([fact.c.state_code], from_obj=[fact])
            pii = PII(connection, RolesConstants.PII)
            query = pii.add_context(get_unittest_tenant_name(), self.user, query)
            result = connection.get_result(query)
            self.assertEqual(238, len(result))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
