'''
Created on Nov 5, 2013

@author: ejen
'''
from pyramid.testing import DummyRequest
from pyramid import testing
from edauth.security.session import Session
from smarter.security.roles.default import DefaultRole  # @UnusedImport
from edcore.tests.utils.unittest_with_edcore_sqlite import \
    Unittest_with_edcore_sqlite,\
    UnittestEdcoreDBConnection, get_unittest_tenant_name
from smarter.extract.processor import process_extraction_request, has_data,\
    get_file_path, get_extract_work_zone_path,\
    get_encryption_public_key_identifier, get_archive_file_path, get_gatekeeper,\
    get_pickup_zone_info
from sqlalchemy.sql.expression import select
from pyramid.registry import Registry


class TestProcessor(Unittest_with_edcore_sqlite):

    def setUp(self):
        self.reg = Registry()
        self.reg.settings = {'extract.work_zone_base_dir': '/tmp/work_zone',
                             'pickup.gatekeeper.t1': '/t/acb',
                             'pickup.gatekeeper.t2': '/a/df',
                             'pickup.gatekeeper.y': '/a/c',
                             'pickup.sftp.hostname': 'hostname.local.net',
                             'pickup.sftp.user': 'myUser',
                             'pickup.sftp.private_key_file': '/home/users/myUser/.ssh/id_rsa'}
        # Set up user context
        self.__request = DummyRequest()
        # Must set hook_zca to false to work with unittest_with_sqlite
        self.__config = testing.setUp(registry=self.reg, request=self.__request, hook_zca=False)
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
        tasks = results['tasks']
        self.assertEqual(len(tasks), 4)
        self.assertEqual(tasks[0]['status'], 'fail')
        self.assertEqual(tasks[3]['status'], 'fail')

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
        path = get_file_path(params, 'tenant', 'request_id')
        self.assertIn('/tmp/work_zone/tenant/request_id/csv/ASMT_CA_UUUU_ABC_', path)
        self.assertIn('.csv.gpg', path)

    def test_get_extract_work_zone_path(self):
        path = get_extract_work_zone_path('tenant', 'request')
        self.assertEqual(path, '/tmp/work_zone/tenant/request/csv')

    def test_get_encryption_public_key_identifier(self):
        self.assertIsNone(get_encryption_public_key_identifier("tenant"))

    def test_get_archive_file_path(self):
        self.assertIn("/tmp/work_zone/tenant/requestId/zip/user", get_archive_file_path("user", "tenant", "requestId"))

    def test_gatekeeper(self):
        config = self.reg.settings
        pickup = config.get('pickup.gatekeeper.t1')
        self.assertEqual(pickup, get_gatekeeper('t1'))
        self.assertEqual(None, get_gatekeeper('dne'))

    def test_get_pickup_zone_info(self):
        config = self.reg.settings
        host = config.get('pickup.sftp.hostname')
        user = config.get('pickup.sftp.user')
        private_key = config.get('pickup.sftp.private_key_file')
        pickup = get_pickup_zone_info('t1')
        self.assertEqual(host, pickup[0])
        self.assertEqual(user, pickup[1])
        self.assertEqual(private_key, pickup[2])
