'''
Created on May 17, 2013

@author: tosako
'''
import unittest
import os

from pyramid import testing
from pyramid.registry import Registry
from pyramid.testing import DummyRequest
from pyramid.security import Allow
from edcore.tests.utils.unittest_with_edcore_sqlite import Unittest_with_edcore_sqlite,\
    get_unittest_tenant_name
from edapi.exceptions import NotFoundException
from smarter.reports.helpers.ISR_pdf_name_formatter import generate_isr_report_path_by_student_id, \
    generate_isr_absolute_file_path_name
from edauth.tests.test_helper.create_session import create_test_session
import edauth
from smarter_common.security.constants import RolesConstants
from edcore.security.tenant import set_tenant_map
from smarter.security.roles.pii import PII  # @UnusedImport
from smarter.reports.helpers.constants import AssessmentType


class TestISRPdfNameFormatter(Unittest_with_edcore_sqlite):

    def setUp(self):
        self.__request = DummyRequest()
        reg = Registry()
        reg.settings = {}
        reg.settings['cache.expire'] = 10
        reg.settings['cache.regions'] = 'session'
        reg.settings['cache.type'] = 'memory'
        self.__config = testing.setUp(registry=reg, request=self.__request, hook_zca=False)
        defined_roles = [(Allow, RolesConstants.PII, ('view', 'logout'))]
        edauth.set_roles(defined_roles)
        set_tenant_map({get_unittest_tenant_name(): 'NC'})
        # Set up context security
        dummy_session = create_test_session([RolesConstants.PII])
        self.__config.testing_securitypolicy(dummy_session.get_user())

    def test_generate_isr_report_path_by_student_id(self):
        file_name = generate_isr_report_path_by_student_id('NC', '20160410', '2016', pdf_report_base_dir='/', student_ids='61ec47de-e8b5-4e78-9beb-677c44dd9b50')
        self.assertEqual(len(file_name), 1)
        self.assertEqual(file_name['61ec47de-e8b5-4e78-9beb-677c44dd9b50'], {'20160410': os.path.join('/', 'NC', '2016', '228', '242', '04', 'isr', 'SUMMATIVE', '61ec47de-e8b5-4e78-9beb-677c44dd9b50.20160410.en.g.pdf')})

    def test_generate_isr_report_path_by_student_id_for_iab(self):
        file_name = generate_isr_report_path_by_student_id('NC', asmt_year=2015, pdf_report_base_dir='/', student_ids='34b99412-fd5b-48f0-8ce8-f8ca3788634a', asmt_type=AssessmentType.INTERIM_ASSESSMENT_BLOCKS)
        self.assertEqual(len(file_name), 1)
        self.assertEqual(file_name['34b99412-fd5b-48f0-8ce8-f8ca3788634a'], {None: os.path.join('/', 'NC', '2015', '229', '936', 'isr', 'INTERIM ASSESSMENT BLOCKS', '34b99412-fd5b-48f0-8ce8-f8ca3788634a.en.g.pdf')})

    def test_generate_isr_report_path_by_student_id_studentguid_not_exist(self):
        self.assertRaises(NotFoundException, generate_isr_report_path_by_student_id, 'NC', '20120101', pdf_report_base_dir='/', student_ids='ff1c2b1a-c15d-11e2-ae11-3c07546832b4')

    def test_generate_isr_absolute_file_path_name(self):
        file_name = generate_isr_absolute_file_path_name(pdf_report_base_dir='/', state_code='FL', asmt_period_year='2013', district_id='123', school_id='456', asmt_grade='01', student_id='1bc-def-ad', asmt_type='SUMMATIVE', date_taken='20120201')
        self.assertEqual(file_name, os.path.join('/', 'FL', '2013', '123', '456', '01', 'isr', 'SUMMATIVE', '1bc-def-ad.20120201.en.pdf'))

    def test_generate_isr_report_path_by_student_id_for_color(self):
        file_name = generate_isr_report_path_by_student_id('NC', '20160410', '2016', pdf_report_base_dir='/', student_ids='61ec47de-e8b5-4e78-9beb-677c44dd9b50', grayScale=False, lang='jp')
        self.assertEqual(len(file_name), 1)
        self.assertEqual(file_name['61ec47de-e8b5-4e78-9beb-677c44dd9b50'], {'20160410': os.path.join('/', 'NC', '2016', '228', '242', '04', 'isr', 'SUMMATIVE', '61ec47de-e8b5-4e78-9beb-677c44dd9b50.20160410.jp.pdf')})

    def test_generate_isr_report_path_by_student_id_studentguid_not_existd_for_color(self):
        self.assertRaises(NotFoundException, generate_isr_report_path_by_student_id, 'NC', '20120201', pdf_report_base_dir='/', student_ids='ff1c2b1a-c15d-11e2-ae11-3c07546832b4', grayScale=False)

    def test_generate_isr_absolute_file_path_named_for_color(self):
        file_name = generate_isr_absolute_file_path_name(pdf_report_base_dir='/', state_code='FL', asmt_period_year='2013', district_id='123', school_id='456', asmt_grade='01', student_id='1bc-def-ad', asmt_type='SUMMATIVE', grayScale=False, date_taken='20120201')
        self.assertEqual(file_name, os.path.join('/', 'FL', '2013', '123', '456', '01', 'isr', 'SUMMATIVE', '1bc-def-ad.20120201.en.pdf'))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
