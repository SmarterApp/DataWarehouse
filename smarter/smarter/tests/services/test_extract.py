'''
Created on Nov 8, 2013

@author: dip
'''
import unittest
from pyramid.testing import DummyRequest
from pyramid import testing
from edcore.tests.utils.unittest_with_edcore_sqlite import Unittest_with_edcore_sqlite,\
    UnittestEdcoreDBConnection, get_unittest_tenant_name
from pyramid.registry import Registry
from edauth.security.session import Session
from smarter.security.roles.school_admin import SchoolAdmin  # @UnusedImport
from edextract.celery import setup_celery
from edapi.httpexceptions import EdApiHTTPPreconditionFailed
from pyramid.response import Response
from smarter.extract.constants import Constants
from smarter.services.extract import post_extract_service, get_extract_service


class TestExtract(Unittest_with_edcore_sqlite):

    def setUp(self):
        self.__request = DummyRequest()
        # Must set hook_zca to false to work with uniittest_with_sqlite
        reg = Registry()
        reg.settings = {}
        self.__config = testing.setUp(registry=reg, request=self.__request, hook_zca=False)
        self.__tenant_name = get_unittest_tenant_name()
        with UnittestEdcoreDBConnection() as connection:
            # Insert into user_mapping table
            user_mapping = connection.get_table('user_mapping')
            connection.execute(user_mapping.insert(), user_id='1023', guid='1023')
        dummy_session = Session()
        dummy_session.set_roles(['SCHOOL_EDUCATION_ADMINISTRATOR_1'])
        dummy_session.set_uid('1023')
        dummy_session.set_tenant(self.__tenant_name)
        self.__config.testing_securitypolicy(dummy_session)
        # celery settings for UT
        settings = {'extract.celery.CELERY_ALWAYS_EAGER': True}
        setup_celery(settings)

    def tearDown(self):
        self.__request = None
        testing.tearDown()
        # delete user_mapping entries
        with UnittestEdcoreDBConnection() as connection:
            user_mapping = connection.get_table('user_mapping')
            connection.execute(user_mapping.delete())

    def test_post_invalid_payload(self):
        self.assertRaises(EdApiHTTPPreconditionFailed, post_extract_service)

    def test_post_post_invalid_param(self):
        self.__request.json_body = {}
        self.assertRaises(EdApiHTTPPreconditionFailed, post_extract_service, self.__request)

    def test_post_valid_response(self):
        self.__request.method = 'POST'
        self.__request.json_body = {'stateCode': ['CA'],
                                    'asmtYear': ['2015'],
                                    'asmtType': ['SUMMATIVE'],
                                    'asmtSubject': ['Math'],
                                    'extractType': ['studentAssessment']}
        dummy_session = Session()
        dummy_session.set_roles(['SCHOOL_EDUCATION_ADMINISTRATOR_1'])
        dummy_session.set_uid('1023')
        dummy_session.set_tenant(self.__tenant_name)
        self.__config.testing_securitypolicy(dummy_session)
        results = post_extract_service(None, self.__request)
        self.assertIsInstance(results, Response)
        self.assertEqual(len(results.json_body['tasks']), 1)
        self.assertEqual(results.json_body['tasks'][0][Constants.STATUS], Constants.FAIL)

    def test_get_invalid_param(self):
        self.__request.GET['stateCode'] = 'NY'
        self.__request.GET['asmyType'] = 'SUMMATIVE'
        self.__request.GET['asmtSubject'] = 'Math'
        self.__request.GET['extractType'] = 'studentAssessment'
        self.assertRaises(EdApiHTTPPreconditionFailed, get_extract_service)

    def test_post_valid_response_failed_task(self):
        self.__request.GET['stateCode'] = 'NY'
        self.__request.GET['asmtType'] = 'SUMMATIVE'
        self.__request.GET['asmtSubject'] = 'Math'
        self.__request.GET['asmtYear'] = '2010'
        self.__request.GET['extractType'] = 'studentAssessment'
        dummy_session = Session()
        dummy_session.set_roles(['SCHOOL_EDUCATION_ADMINISTRATOR_1'])
        dummy_session.set_uid('1023')
        dummy_session.set_tenant(self.__tenant_name)
        self.__config.testing_securitypolicy(dummy_session)
        results = get_extract_service(None, self.__request)
        self.assertIsInstance(results, Response)
        tasks = results.json_body['tasks']
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0][Constants.STATUS], Constants.FAIL)

    def test_multi_tasks(self):
        self.__request.method = 'POST'
        self.__request.json_body = {'stateCode': ['CA'],
                                    'asmtYear': ['2015', '2011'],
                                    'asmtType': ['SUMMATIVE'],
                                    'asmtSubject': ['Math', 'ELA'],
                                    'extractType': ['studentAssessment']}
        dummy_session = Session()
        dummy_session.set_roles(['SCHOOL_EDUCATION_ADMINISTRATOR_1'])
        dummy_session.set_uid('1023')
        dummy_session.set_tenant(self.__tenant_name)
        self.__config.testing_securitypolicy(dummy_session)
        results = post_extract_service(None, self.__request)
        self.assertIsInstance(results, Response)
        tasks = results.json_body['tasks']
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0][Constants.STATUS], Constants.FAIL)
        self.assertEqual(tasks[1][Constants.STATUS], Constants.FAIL)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
