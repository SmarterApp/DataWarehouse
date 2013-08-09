'''
Created on Jul 16, 2013

@author: tosako
'''
import unittest
from smarter.reports.filters import Constants_filter_names
from smarter.reports.filters.Constants_filter_names import DEMOGRAPHICS_PROGRAM_IEP
from sqlalchemy.sql.expression import true, false, null
from smarter.reports.filters.demographics import get_demographic_filter
from smarter.tests.utils.unittest_with_smarter_sqlite import Unittest_with_smarter_sqlite_no_data_load


class TestDemographics(Unittest_with_smarter_sqlite_no_data_load):

    def test_get_demographic_program_filter(self):
        test_filter = {}
        value = get_demographic_filter(DEMOGRAPHICS_PROGRAM_IEP, None, test_filter)
        self.assertFalse(value)
        test_filter = {DEMOGRAPHICS_PROGRAM_IEP: [Constants_filter_names.YES]}
        value = get_demographic_filter(DEMOGRAPHICS_PROGRAM_IEP, True, test_filter)
        self.assertEqual(str(value), str(True == true()))
        test_filter = {DEMOGRAPHICS_PROGRAM_IEP: [Constants_filter_names.NO]}
        value = get_demographic_filter(DEMOGRAPHICS_PROGRAM_IEP, False, test_filter)
        self.assertEqual(str(value), str(False == false()))
        test_filter = {DEMOGRAPHICS_PROGRAM_IEP: [Constants_filter_names.NOT_STATED]}
        value = get_demographic_filter(DEMOGRAPHICS_PROGRAM_IEP, None, test_filter)
        self.assertEqual(str(value), str(None == null()))
        test_filter = {DEMOGRAPHICS_PROGRAM_IEP: [Constants_filter_names.YES, Constants_filter_names.NO, Constants_filter_names.NOT_STATED]}
        value = get_demographic_filter(DEMOGRAPHICS_PROGRAM_IEP, None, test_filter)
        self.assertEqual(3, len(value))
        test_filter = {DEMOGRAPHICS_PROGRAM_IEP: [Constants_filter_names.YES, 'whatever']}
        value = get_demographic_filter(DEMOGRAPHICS_PROGRAM_IEP, True, test_filter)
        self.assertEqual(str(value), str(True == true()))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_value_NONE']
    unittest.main()
