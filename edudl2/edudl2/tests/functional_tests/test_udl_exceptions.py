from edudl2.exceptions.errorcodes import ErrorSource
from edudl2.exceptions.udl_exceptions import UDLDataIntegrityError,\
    DeleteRecordNotFound
from edudl2.tests.functional_tests.util import UDLTestHelper
from edudl2.database.udl2_connector import get_udl_connection
from sqlalchemy import select
import datetime


class UDLExceptionTest(UDLTestHelper):

    @classmethod
    def setUpClass(cls):
        super(UDLExceptionTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(UDLExceptionTest, cls).tearDownClass()

    def setUp(self):
        super(UDLExceptionTest, self).truncate_udl_tables()
        self.guid_batch = '2411183a-dfb7-42f7-9b3e-bb7a597aa3e7'
        self.insert_error_message = 'Data integrity violence found for batch: test_batch_guid_1 in schema.table, ' +\
            'error message: (IntegrityError) duplicate key value violates unique constraint "fact_asmt_outcome_vw_pkey"\n' +\
            'DETAIL:  Key (asmt_outcome_vw_rec_id)=(11339) already exists.\n' +\
            ' \'UPDATE "edware"."fact_asmt_outcome_vw" ' +\
            'SET asmt_outcome_vw_rec_id = %(asmt_outcome_vw_rec_id)s, ' +\
            'status = %(new_status)s WHERE batch_guid = %(batch_guid)s ' +\
            'AND asmt_guid = %(asmt_guid_1)s AND ' +\
            "status = %(status)s AND student_id = %(student_id_1)s' " +\
            "{'status': 'W', 'student_id_1': '60ca47b5-527e-4cb0-898d-f754fd7099a0', " +\
            "'asmt_outcome_vw_rec_id': 11339, 'batch_guid': 'c9b8baa3-0353-40a7-9618-1aaf8befae0e', " +\
            "'new_status': 'D', 'asmt_guid_1': '7b7a8b43-17dc-4a0b-a37e-6170c08894a5'}"
        self.error_source_delete_twice = ErrorSource.DELETE_FACT_ASMT_OUTCOME_RECORD_MORE_THAN_ONCE
        self.error_source_mismatched = ErrorSource.MISMATCHED_FACT_ASMT_OUTCOME_RECORD
        self.schema_table = '"edware_sds_1_12"."fact_asmt_outcome_vw"'
        self.udl_phase_step = "Handle Deletion"
        self.working_schema = "edware"
        self.mismatched_rows = [{'asmt_outcome_vw_rec_id': 1000,
                                 'asmt_guid': '7b7a8b43-17dc-4a0b-a37e-6170c08894a5',
                                 'student_id': '60ca47b5-527e-4cb0-898d-f754fd7099a0'}]

    def tearDown(self):
        super(UDLExceptionTest, self).truncate_udl_tables()

    def get_err_list(self):
        with get_udl_connection() as conn:
            err_list_table = conn.get_table('err_list')
            query = select([err_list_table]).where(err_list_table.c['guid_batch'].__eq__(self.guid_batch))
            result = conn.get_result(query)
            return result

    def get_udl_batch(self):
        with get_udl_connection() as conn:
            batch_table = conn.get_table('udl_batch')
            query = select([batch_table]).where(batch_table.c['guid_batch'].__eq__(self.guid_batch))
            result = conn.get_result(query)
            return result

    def test_insert_err_list_integrity_error(self):
        exc = UDLDataIntegrityError(self.guid_batch, self.insert_error_message, self.schema_table,
                                    self.error_source_delete_twice, self.udl_phase_step, self.working_schema)
        exc.insert_err_list('20140303')
        errors = self.get_err_list()
        self.assertEqual(1, len(errors))
        self.assertEqual(errors[0]['record_sid'], 11339)
        self.assertEqual(errors[0]['guid_batch'], '2411183a-dfb7-42f7-9b3e-bb7a597aa3e7')
        self.assertEqual(errors[0]['err_code'], 1001)
        self.assertEqual(errors[0]['err_source'], 2)
        self.assertEqual(errors[0]['err_code_text'], 'DATA_INTEGRITY_ERROR')
        self.assertEqual(errors[0]['err_source_text'], 'DELETE_FACT_ASMT_OUTCOME_RECORD_MORE_THAN_ONCE')
        self.assertEqual(errors[0]['created_date'], datetime.datetime(2014, 3, 3, 0, 0))
        self.assertEqual(errors[0]['err_input'], 'student_id:60ca47b5-527e-4cb0-898d-f754fd7099a0, asmt_guid:7b7a8b43-17dc-4a0b-a37e-6170c08894a5')

    def test_insert_err_list__delete_record_not_found(self):
        exc = DeleteRecordNotFound(self.guid_batch, self.mismatched_rows, self.schema_table,
                                   self.error_source_mismatched, self.udl_phase_step, self.working_schema, 'asmt_outcome_vw_rec_id')
        exc.insert_err_list('20140303')
        self.get_err_list()
        errors = self.get_err_list()
        self.assertEqual(1, len(errors))
        self.assertEqual(errors[0]['record_sid'], 1000)
        self.assertEqual(errors[0]['guid_batch'], '2411183a-dfb7-42f7-9b3e-bb7a597aa3e7')
        self.assertEqual(errors[0]['err_code'], 1000)
        self.assertEqual(errors[0]['err_source'], 1)
        self.assertEqual(errors[0]['err_code_text'], 'DELETE_RECORD_NOT_FOUND')
        self.assertEqual(errors[0]['err_source_text'], 'MISMATCHED_FACT_ASMT_OUTCOME_RECORD')
        self.assertEqual(errors[0]['created_date'], datetime.datetime(2014, 3, 3, 0, 0))
        self.assertEqual(errors[0]['err_input'], 'student_id:60ca47b5-527e-4cb0-898d-f754fd7099a0, asmt_guid:7b7a8b43-17dc-4a0b-a37e-6170c08894a5')
