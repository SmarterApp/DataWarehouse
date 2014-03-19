'''
Created on Mar 4, 2014

@author: sravi
'''
from edcore.tests.utils.unittest_with_edcore_sqlite import Unittest_with_edcore_sqlite, \
    UnittestEdcoreDBConnection, get_unittest_tenant_name
from sqlalchemy.sql.expression import select
from sqlalchemy import func
import edcore.utils.cleanup as cleanup
from edcore.utils.utils import compile_query_to_sql_text


class TestCleanup(Unittest_with_edcore_sqlite):

    def setUp(self):
        self._tenant = get_unittest_tenant_name()
        self.dim_tables = ['dim_asmt', 'dim_inst_hier', 'dim_section', 'dim_student']
        self.fact_tables = ['fact_asmt_outcome']
        self.other_tables = ['custom_metadata', 'user_mapping', 'student_reg']

    @classmethod
    def setUpClass(cls):
        Unittest_with_edcore_sqlite.setUpClass()

    def tearDown(self):
        pass

    def _verify_all_records_deleted_by_batch_guid(self, connection, table, batch_guid):
        fao = connection.get_table(table)
        query = select([func.count(fao.c.asmnt_outcome_rec_id)], from_obj=[fao])
        query = query.where(fao.c.batch_guid == batch_guid)
        results = connection.execute(query)
        fao_rows = results.first()
        self.assertEquals(0, fao_rows[0])

    def test_get_filtered_dim_tables(self):
        with UnittestEdcoreDBConnection() as connection:
            all_tables = cleanup.get_filtered_tables(connection, 'dim_')
            self.assertEquals(4, len(all_tables))
            self.assertTrue(len(set(all_tables).intersection(self.dim_tables)) > 0)

    def test_get_filtered_fact_tables(self):
        with UnittestEdcoreDBConnection() as connection:
            all_tables = cleanup.get_filtered_tables(connection, 'fact_')
            self.assertEquals(1, len(all_tables))
            self.assertTrue(len(set(all_tables).intersection(self.fact_tables)) > 0)

    def test_get_filtered_all_tables(self):
        with UnittestEdcoreDBConnection() as connection:
            all_tables = cleanup.get_filtered_tables(connection)
            self.assertEquals(7, len(all_tables))
            self.assertTrue(len(set(all_tables).intersection(self.dim_tables
                            + self.fact_tables + self.other_tables)) > 0)

    def test_cleanup_all_tables_with_prefix_for_valid_batch_guid(self):
        with UnittestEdcoreDBConnection() as connection:
            test_batch_guid = '90901b70-ddaa-11e2-a95d-68a86d3c2f82'
            cleanup.cleanup_all_tables(connection, 'batch_guid', test_batch_guid, False, table_name_prefix='fact_')
            self._verify_all_records_deleted_by_batch_guid(connection, 'fact_asmt_outcome', test_batch_guid)

    def test_cleanup_all_tables_for_valid_batch_guid(self):
        with UnittestEdcoreDBConnection() as connection:
            test_batch_guid = '90901b70-ddaa-11e2-a95d-68a86d3c2f82'
            cleanup.cleanup_all_tables(connection, 'batch_guid', test_batch_guid, False, tables=['fact_asmt_outcome'])
            self._verify_all_records_deleted_by_batch_guid(connection, 'fact_asmt_outcome', test_batch_guid)

    def test_get_schema_check_query(self):
        expected_query = "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'test_schema'"
        query = cleanup._get_schema_check_query('test_schema')
        query_string = str(compile_query_to_sql_text(query)).replace("\n", "")
        self.assertEquals(query_string, expected_query)
