'''
Created on Nov 5, 2013

@author: ejen
'''
from pyramid.testing import DummyRequest
from pyramid import testing
from edauth.security.session import Session
from smarter.security.roles.teacher import Teacher  # @UnusedImport
from edcore.tests.utils.unittest_with_edcore_sqlite import \
    Unittest_with_edcore_sqlite,\
    UnittestEdcoreDBConnection, get_unittest_tenant_name
from smarter.extract.processor import process_extraction_request, has_data,\
    get_file_name
from sqlalchemy.sql.expression import select


class TestProcessor(Unittest_with_edcore_sqlite):

    def setUp(self):
        # Set up user context
        self.__request = DummyRequest()
        # Must set hook_zca to false to work with unittest_with_sqlite
        self.__config = testing.setUp(request=self.__request, hook_zca=False)
        # Set up context security
        with UnittestEdcoreDBConnection() as connection:
            # Insert into user_mapping table
            user_mapping = connection.get_table('user_mapping')
            connection.execute(user_mapping.insert(),
                               user_id='272', guid='272')
        dummy_session = Session()
        dummy_session.set_roles(['STATE_EDUCATION_ADMINISTRATOR_1'])
        dummy_session.set_uid('272')
        dummy_session.set_tenant(get_unittest_tenant_name())
        self.__config.testing_securitypolicy(dummy_session)

    def tearDown(self):
        # reset the registry
        testing.tearDown()

        # delete user_mapping entries
        with UnittestEdcoreDBConnection() as connection:
            user_mapping = connection.get_table('user_mapping')
            connection.execute(user_mapping.delete())

    def test_process_extraction_request(self):
        params = {'stateCode': ['CA'],
                  'asmtYear': ['2015'],
                  'asmtType': ['SUMMATIVE', 'COMPREHENSIVE INTERIM'],
                  'asmtSubject': ['Math', 'ELA'],
                  'extractType': ['studentAssessment']}
        results = process_extraction_request(params)
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]['status'], 'fail')
        self.assertEqual(results[3]['status'], 'fail')

    def test_has_data_false(self):
        with UnittestEdcoreDBConnection() as connection:
            fact = connection.get_table('fact_asmt_outcome')
            query = select([fact.c.state_code], from_obj=[fact])
            query = query.where(fact.c.state_code == 'UT')
            self.assertFalse(has_data(query, '1'))

    def test_has_data_true(self):
        with UnittestEdcoreDBConnection() as connection:
            fact = connection.get_table('fact_asmt_outcome')
            query = select([fact.c.state_code], from_obj=[fact])
            query = query.where(fact.c.state_code == 'NY')
            self.assertTrue(has_data(query, '1'))

    def test_get_file_name(self):
        params = {'stateCode': 'CA',
                  'asmtSubject': 'UUUU',
                  'asmtType': 'abc'}
        self.assertEqual('ASMT_CA_UUUU_ABC_', get_file_name(params))
