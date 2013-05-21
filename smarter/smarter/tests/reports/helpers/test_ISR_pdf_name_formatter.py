'''
Created on May 17, 2013

@author: tosako
'''
import unittest
from smarter.tests.utils.unittest_with_smarter_sqlite import Unittest_with_smarter_sqlite
from edapi.exceptions import NotFoundException
import os
from smarter.reports.helpers.ISR_pdf_name_formatter import generate_isr_report_path_by_student_guid, \
    generate_isr_absolute_file_path_name


class Test(Unittest_with_smarter_sqlite):

    def test_generate_isr_report_path_by_student_guid(self):
        file_name = generate_isr_report_path_by_student_guid(pdf_report_base_dir='/', student_guid='61ec47de-e8b5-4e78-9beb-677c44dd9b50')
        self.assertEqual(file_name, os.path.join('/', 'NY', '2012', '228', '242', '3', 'isr', 'SUMMATIVE', '61ec47de-e8b5-4e78-9beb-677c44dd9b50.pdf'))

    def test_generate_isr_report_path_by_student_guid_studentguid_not_exist(self):
        self.assertRaises(NotFoundException, generate_isr_report_path_by_student_guid, pdf_report_base_dir='/', student_guid='ff1c2b1a-c15d-11e2-ae11-3c07546832b4')

    def test_generate_isr_absolute_file_path_name(self):
        file_name = generate_isr_absolute_file_path_name(pdf_report_base_dir='/', state_code='FL', asmt_period_year='2013', district_guid='123', school_guid='456', asmt_grade='1', student_guid='1bc-def-ad', asmt_type='SUMMATIVE')
        self.assertEqual(file_name, os.path.join('/', 'FL', '2013', '123', '456', '1', 'isr', 'SUMMATIVE', '1bc-def-ad.pdf'))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
