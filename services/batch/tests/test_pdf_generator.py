# (c) 2014 Amplify Education, Inc. All rights reserved, subject to the license
# below.
#
# Education agencies that are members of the Smarter Balanced Assessment
# Consortium as of August 1, 2014 are granted a worldwide, non-exclusive, fully
# paid-up, royalty-free, perpetual license, to access, use, execute, reproduce,
# display, distribute, perform and create derivative works of the software
# included in the Reporting Platform, including the source code to such software.
# This license includes the right to grant sublicenses by such consortium members
# to third party vendors solely for the purpose of performing services on behalf
# of such consortium member educational agencies.

'''
Created on Jun 22, 2013

@author: dip
'''
import unittest
from services.celery import setup_celery
from zope import component
from edauth.security.session_backend import ISessionBackend, SessionBackend
from batch.pdf.pdf_generator import PDFGenerator
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import tempfile
import shutil
import os
import services
from services.tasks.pdf import prepare_path
from urllib.parse import urlparse, parse_qs


class TestPdfGenerator(unittest.TestCase):

    def setUp(self):
        self.__temp_dir = tempfile.mkdtemp()

        self.settings = {}
        self.settings['cache.regions'] = 'public.data, session'
        self.settings['cache.type'] = 'memory'
        self.settings['batch.user.session.timeout'] = 10777700
        self.settings['auth.policy.secret'] = 'secret'
        self.settings['auth.policy.cookie_name'] = 'myName'
        self.settings['auth.policy.hashalg'] = 'sha1'
        self.settings['application.url'] = 'dummy:1234'
        self.settings['services.celery.CELERY_ALWAYS_EAGER'] = True
        self.settings['pdf.base.url'] = 'http://dummy:8234'
        self.settings['pdf.batch.job.queue'] = 'dummyQueue'
        self.settings['pdf.health_check.job.queue'] = 'dummyQueue'
        self.settings['pdf.report_base_dir'] = self.__temp_dir
        self.settings['pdf.minimum_file_size'] = 0

        CacheManager(**parse_cache_config_options(self.settings))

        setup_celery(self.settings)

        component.provideUtility(SessionBackend(self.settings), ISessionBackend)
        self.pdf_generator = PDFGenerator(self.settings, 'myTenant')

    def tearDown(self):
        component.provideUtility(None, ISessionBackend)
        shutil.rmtree(self.__temp_dir, ignore_errors=True)

    def test_instantiation(self):
        self.assertIsNotNone(self.pdf_generator.settings)
        self.assertEqual(self.pdf_generator.tenant, 'myTenant')
        self.assertEqual(self.pdf_generator.cookie_name, 'myName')
        self.assertIsNotNone(self.pdf_generator.cookie_value)

    def test_send_pdf_request(self):
        # Override the wkhtmltopdf command
        services.tasks.pdf.pdf_procs = ['echo', 'dummy']
        pdf_file = os.path.join(self.__temp_dir, 'test.pdf')
        prepare_path(pdf_file)
        with open(pdf_file, 'w') as file:
            file.write('%PDF-1.4')
        results = self.pdf_generator.send_pdf_request('student-guid', 'ny', '2012', 'SUMMATIVE', '20120201', pdf_file)
        self.assertIsNotNone(results.task_id)
        self.assertEqual(results.status, 'SUCCESS')

    def test_build_url(self):
        student_id = '2343'
        report = 'ISR.html'
        effective_date = '20120201'
        results = self.pdf_generator.build_url(student_id, 'ny', '2012', 'SUMMATIVE', effective_date, report)
        url = urlparse(results)
        self.assertEqual(url.scheme + "://" + url.netloc + url.path, self.settings['pdf.base.url'] + '/' + report)
        query_param = parse_qs(url.query)
        self.assertEqual(len(query_param.keys()), 6)
        self.assertEqual(query_param['studentId'][0], student_id)
        self.assertEqual(query_param['pdf'][0], 'true')
        self.assertEqual(query_param['asmtYear'][0], '2012')
        self.assertEqual(query_param['asmtType'][0], 'SUMMATIVE')

    def test_build_url_with_trailing_slash(self):
        self.settings['pdf.base.url'] = 'http://dummy:8234/reports/'

        self.pdf_generator = PDFGenerator(self.settings, 'myTenant')
        student_id = '2343'
        report = 'ISR.html'
        effective_date = '20120201'
        results = self.pdf_generator.build_url(student_id, 'ny', '2012', 'SUMMATIVE', effective_date, report)
        url = urlparse(results)
        self.assertEqual(url.scheme + "://" + url.netloc + url.path, self.settings['pdf.base.url'] + report)
        query_param = parse_qs(url.query)
        self.assertEqual(len(query_param.keys()), 6)
        self.assertEqual(query_param['studentId'][0], student_id)
        self.assertEqual(query_param['pdf'][0], 'true')
        self.assertEqual(query_param['stateCode'][0], 'ny')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
