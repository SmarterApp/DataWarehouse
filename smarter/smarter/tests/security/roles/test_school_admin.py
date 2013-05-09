'''
Created on May 9, 2013

@author: dip
'''
import unittest
from smarter.tests.utils.unittest_with_smarter_sqlite import Unittest_with_smarter_sqlite
from smarter.database.connector import SmarterDBConnection
from sqlalchemy.sql.expression import select
from smarter.reports.helpers.constants import Constants
from smarter.security.roles.school_admin import SchoolAdmin


class TestSchoolAdminContextSecurity(Unittest_with_smarter_sqlite):

    def test_get_school_admin_context(self):
        guid = "1023"
        with SmarterDBConnection() as connection:
            school_admin = SchoolAdmin(connection)
            context = school_admin.get_context(guid)
            self.assertListEqual(context, ['939'])

    def test_get_school_admin_invalid_guid(self):
        guid = "invalid-guid"
        with SmarterDBConnection() as connection:
            school_admin = SchoolAdmin(connection)
            context = school_admin.get_context(guid)
            self.assertListEqual(context, [])

    def test_append_school_admin_context(self):
        with SmarterDBConnection() as connection:
            guid = '1023'
            fact_asmt_outcome = connection.get_table(Constants.FACT_ASMT_OUTCOME)
            query = select([fact_asmt_outcome.c.school_guid],
                           from_obj=([fact_asmt_outcome]))
            school_admin = SchoolAdmin(connection)
            query = school_admin.append_context(query, guid)

            results = connection.get_result(query)
            self.assertTrue(len(results) > 0)
            for result in results:
                self.assertEqual(result[Constants.SCHOOL_GUID], '939')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
