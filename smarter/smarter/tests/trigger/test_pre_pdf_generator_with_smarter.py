'''
Created on Jun 24, 2013

@author: dip
'''
import unittest
from smarter.tests.utils.unittest_with_smarter_sqlite import Unittest_with_smarter_sqlite,\
    get_unittest_tenant_name
from smarter.trigger.pre_pdf_generator import prepare_pre_pdf, trigger_pre_pdf
import services
from zope import component
from edauth.security.session_backend import ISessionBackend, SessionBackend
from services.celery import setup_celery


class TestPrePdfGenerator(Unittest_with_smarter_sqlite):

    def setUp(self):
        self.tenant = get_unittest_tenant_name()

    def tearDown(self):
        pass

    def test_prepare_pre_pdf(self):
        results = prepare_pre_pdf(self.tenant, 'NY', '820568d0-ddaa-11e2-a63d-68a86d3c2f82')
        self.assertEqual(58, len(results))
        results = prepare_pre_pdf(self.tenant, 'NY', '90901b70-ddaa-11e2-a95d-68a86d3c2f82')
        self.assertEqual(118, len(results))
        results = prepare_pre_pdf(self.tenant, 'NY', 'd2d02660-ddd7-11e2-a28f-0800200c9a66')
        self.assertEqual(2, len(results))

    def test_prepare_pre_pdf_with_future_date(self):
        results = prepare_pre_pdf(self.tenant, 'NY', 'd1d7d814-ddb1-11e2-b3dd-68a86d3c2f82')
        self.assertEqual(0, len(results))

    def test_trigger_pre_pdf_with_empty_results(self):
        triggered = trigger_pre_pdf({}, self.tenant, 'NY', [])
        self.assertFalse(triggered)

    def test_trigger_pre_pdf(self):
        settings = {'pdf.base.url': 'http://dummy:1223',
                    'pdf.batch.job.queue': 'dummy',
                    'batch.user.session.timeout': 10000,
                    'auth.policy.secret': 'dummySecret',
                    'auth.policy.cookie_name': 'dummy',
                    'auth.policy.hashalg': 'sha1',
                    'celery.CELERY_ALWAYS_EAGER': True,
                    'pdf.minimum_file_size': 0,
                    'cache.regions': 'public.data, session',
                    'cache.type': 'memory'
                    }
        component.provideUtility(SessionBackend(settings), ISessionBackend)
        services.tasks.pdf.pdf_procs = ['echo', 'dummy']
        setup_celery(settings)

        results = [{'school_guid': '242', 'district_guid': '228', 'asmt_period_year': 2012, 'asmt_grade': '3', 'student_guid': '34140997-8949-497e-bbbb-5d72aa7dc9cb'}]
        triggered = trigger_pre_pdf(settings, self.tenant, 'NY', results)
        self.assertTrue(triggered)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
