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

from edmigrate.utils.migrate import get_batches_to_migrate, migrate_batch, \
    report_udl_stats_batch_status, migrate_table, cleanup_batch
from edmigrate.tests.utils.unittest_with_preprod_sqlite import Unittest_with_preprod_sqlite, \
    get_unittest_tenant_name as get_unittest_preprod_tenant_name
from edmigrate.exceptions import EdMigrateRecordAlreadyDeletedException, \
    EdMigrateUdl_statException
from sqlalchemy.sql.expression import select, func
from edmigrate.utils.constants import Constants
from edcore.tests.utils.unittest_with_stats_sqlite import Unittest_with_stats_sqlite
from edmigrate.database.migrate_dest_connector import EdMigrateDestConnection
from edmigrate.database.migrate_source_connector import EdMigrateSourceConnection
from edcore.database.utils.constants import UdlStatsConstants, LoadType
from edcore.tests.utils.unittest_with_edcore_sqlite import Unittest_with_edcore_sqlite, \
    get_unittest_tenant_name as get_unittest_prod_tenant_name
from edschema.metadata.util import get_natural_key_columns
import datetime
from edcore.database.utils.query import insert_udl_stats

__author__ = 'sravi'


class TestMigrate(Unittest_with_edcore_sqlite, Unittest_with_preprod_sqlite, Unittest_with_stats_sqlite):

    test_tenant = 'tomcat'

    def setUp(self):
        self.__tenant = TestMigrate.test_tenant

    @classmethod
    def setUpClass(cls):
        Unittest_with_edcore_sqlite.setUpClass(EdMigrateDestConnection.get_datasource_name(TestMigrate.test_tenant),
                                               use_metadata_from_db=False)
        Unittest_with_preprod_sqlite.setUpClass()
        Unittest_with_stats_sqlite.setUpClass()

    def tearDown(self):
        pass

    def insert_into_udl_stats(self, rec_id, guid_batch, load_type, tenant_name):
        udl_stats = {UdlStatsConstants.REC_ID: rec_id,
                     UdlStatsConstants.BATCH_GUID: guid_batch,
                     UdlStatsConstants.LOAD_TYPE: load_type,
                     UdlStatsConstants.FILE_ARRIVED: datetime.datetime.now(),
                     UdlStatsConstants.TENANT: tenant_name,
                     UdlStatsConstants.LOAD_STATUS: UdlStatsConstants.UDL_STATUS_RECEIVED}
        insert_udl_stats(udl_stats)

    def test_migrate_getting_natural_key(self):
        with EdMigrateDestConnection(tenant=get_unittest_prod_tenant_name()) as prod_conn:
            self.assertEquals(get_natural_key_columns(prod_conn.get_table('dim_student')), ['student_id'])
            self.assertEquals(get_natural_key_columns(prod_conn.get_table('dim_asmt')), ['asmt_guid'])
            self.assertEquals(get_natural_key_columns(prod_conn.get_table('fact_asmt_outcome_vw')),
                              ['asmt_guid', 'student_id', 'date_taken'])
            self.assertEquals(get_natural_key_columns(prod_conn.get_table('fact_asmt_outcome')),
                              ['asmt_guid', 'student_id', 'date_taken'])
            self.assertEquals(get_natural_key_columns(prod_conn.get_table('dim_inst_hier')),
                              ['state_code', 'district_id', 'school_id'])

    def test_migrate_fact_asmt_outcome_vw(self):
        preprod_conn = EdMigrateSourceConnection(tenant=get_unittest_preprod_tenant_name())
        prod_conn = EdMigrateDestConnection(tenant=get_unittest_prod_tenant_name())
        batch_guid = "288220EB-3876-41EB-B3A7-F0E6C8BD013B"
        fact_asmt_outcome_table = prod_conn.get_table(Constants.FACT_ASMT_OUTCOME)
        query = select([func.count().label('asmt_outcome_vw_rec_ids')], fact_asmt_outcome_table.c.asmt_outcome_vw_rec_id.in_([1000000776, 1000001034, 1000001112]))
        query_c = query.where(fact_asmt_outcome_table.c.rec_status == 'C')
        query_d = query.where(fact_asmt_outcome_table.c.rec_status == 'D')
        query_I = query.where(fact_asmt_outcome_table.c.rec_status == 'I')
        rset = prod_conn.execute(query_c)
        row = rset.fetchone()
        self.assertEqual(3, row['asmt_outcome_vw_rec_ids'])
        rset.close()
        delete_count, insert_count = migrate_table(batch_guid, None, preprod_conn, prod_conn,
                                                   'fact_asmt_outcome_vw', False)
        self.assertEqual(3, delete_count)
        self.assertEqual(3, insert_count)
        rset = prod_conn.execute(query_c)
        row = rset.fetchone()
        self.assertEqual(0, row['asmt_outcome_vw_rec_ids'])
        rset.close()
        rset = prod_conn.execute(query_d)
        row = rset.fetchone()
        self.assertEqual(3, row['asmt_outcome_vw_rec_ids'])
        rset.close()
        # The deactivation count will be always zero in unit test
        rset = prod_conn.execute(query_I)
        row = rset.fetchone()
        self.assertEqual(0, row['asmt_outcome_vw_rec_ids'])
        rset.close()

    def test_migrate_fact_asmt_outcome_vw_record_already_deleted1(self):
        preprod_conn = EdMigrateSourceConnection(tenant=get_unittest_preprod_tenant_name())
        prod_conn = EdMigrateDestConnection(tenant=get_unittest_prod_tenant_name())
        batch_guid = "288220EB-3876-41EB-B3A7-F0E6C8BD013B"
        self.assertRaises(EdMigrateRecordAlreadyDeletedException, migrate_table, batch_guid, None,
                          preprod_conn, prod_conn, 'fact_asmt_outcome_vw', False)

    def test_migrate_fact_asmt_outcome_vw_record_already_deleted2(self):
        preprod_conn = EdMigrateSourceConnection(tenant=get_unittest_preprod_tenant_name())
        prod_conn = EdMigrateDestConnection(tenant=get_unittest_prod_tenant_name())
        batch_guid = "288220EB-3876-41EB-B3A7-F0E6C8BD013B"
        self.assertRaises(EdMigrateRecordAlreadyDeletedException, migrate_table, batch_guid, None,
                          preprod_conn, prod_conn, 'fact_asmt_outcome_vw', False, batch_size=1)

    def test_migrate_student_reg(self):
        Unittest_with_edcore_sqlite.setUpClass(EdMigrateDestConnection.get_datasource_name(TestMigrate.test_tenant),
                                               use_metadata_from_db=False)
        preprod_conn = EdMigrateSourceConnection(tenant=get_unittest_preprod_tenant_name())
        prod_conn = EdMigrateDestConnection(tenant=get_unittest_prod_tenant_name())
        batch_guid = "0aa942b9-75cf-4055-a67a-8b9ab53a9dfc"
        student_reg_table = preprod_conn.get_table(Constants.STUDENT_REG)
        get_query = select([student_reg_table.c.student_reg_rec_id]).order_by(student_reg_table.c.student_reg_rec_id)
        count_query = select([func.count().label('student_reg_rec_ids')],
                             student_reg_table.c.student_reg_rec_id.in_(range(15541, 15551)))

        rset = preprod_conn.execute(get_query)
        row = rset.fetchall()
        self.assertEqual(10, len(row))
        self.assertListEqual([(15541,), (15542,), (15543,), (15544,), (15545,), (15546,), (15547,), (15548,), (15549,), (15550,)],
                             row)
        rset.close()

        rset = prod_conn.execute(count_query)
        row = rset.fetchone()
        self.assertEqual(0, row['student_reg_rec_ids'])
        rset.close()

        delete_count, insert_count = migrate_table(batch_guid, None, preprod_conn, prod_conn, 'student_reg', False)
        self.assertEqual(0, delete_count)
        self.assertEqual(10, insert_count)

        rset = prod_conn.execute(count_query)
        row = rset.fetchone()
        self.assertEqual(10, row['student_reg_rec_ids'])
        rset.close()

    def test_get_batches_to_migrate_with_specified_tenant(self):
        batches_to_migrate = get_batches_to_migrate('test')
        self.assertEqual(4, len(batches_to_migrate))

    def test_migrate_batch_asmt(self):
        batch_guid = '3384654F-9076-45A6-BB13-64E8EE252A49'
        batch = {UdlStatsConstants.REC_ID: '5',
                 UdlStatsConstants.BATCH_GUID: batch_guid, UdlStatsConstants.TENANT: self.__tenant,
                 UdlStatsConstants.SCHEMA_NAME: None, Constants.DEACTIVATE: False,
                 UdlStatsConstants.LOAD_TYPE: LoadType.ASSESSMENT,
                 UdlStatsConstants.BATCH_OPERATION: None,
                 UdlStatsConstants.SNAPSHOT_CRITERIA: None}
        self.insert_into_udl_stats(batch[UdlStatsConstants.REC_ID], batch_guid, self.__tenant, batch[UdlStatsConstants.LOAD_TYPE])
        rtn = migrate_batch(batch)
        self.assertTrue(rtn)

    def test_migrate_batch_stureg(self):
        batch_guid = '2bb942b9-75cf-4055-a67a-8b9ab53a9dfc'
        batch = {UdlStatsConstants.REC_ID: '6',
                 UdlStatsConstants.BATCH_GUID: batch_guid, UdlStatsConstants.TENANT: self.__tenant,
                 UdlStatsConstants.SCHEMA_NAME: None, Constants.DEACTIVATE: False,
                 UdlStatsConstants.LOAD_TYPE: LoadType.STUDENT_REGISTRATION,
                 UdlStatsConstants.BATCH_OPERATION: 's',
                 UdlStatsConstants.SNAPSHOT_CRITERIA: '{"reg_system_id": "015247bd-058c-48cd-bb4d-f6cffe5b40c1", "academic_year": 2015}'}
        self.insert_into_udl_stats(batch[UdlStatsConstants.REC_ID], batch_guid, self.__tenant, batch[UdlStatsConstants.LOAD_TYPE])

        preprod_conn = EdMigrateSourceConnection(tenant=get_unittest_preprod_tenant_name())
        count_to_source_query = select([func.count()]).select_from(preprod_conn.get_table(Constants.STUDENT_REG))
        count_to_be_inserted = preprod_conn.execute(count_to_source_query).fetchall()[0][0]
        self.assertEqual(10, count_to_be_inserted)

        prod_conn = EdMigrateDestConnection(tenant=get_unittest_preprod_tenant_name())
        student_reg_table = prod_conn.get_table(Constants.STUDENT_REG)
        count_query = select([func.count()]).select_from(student_reg_table)
        count_before = prod_conn.execute(count_query).fetchall()[0][0]
        self.assertEqual(2581, count_before)

        count_snapshot_query = select([func.count()], student_reg_table.c.academic_year == 2015).select_from(student_reg_table)
        count_to_be_deleted = prod_conn.execute(count_snapshot_query).fetchall()[0][0]
        self.assertEqual(1217, count_to_be_deleted)

        rtn = migrate_batch(batch)
        self.assertTrue(rtn)

        expected_count_after = count_before - count_to_be_deleted + count_to_be_inserted
        count_after = prod_conn.execute(count_query).fetchall()[0][0]
        self.assertEqual(expected_count_after, count_after)

    def test_cleanup_batch_asmt(self):
        batch_guid = '3384654F-9076-45A6-BB13-64E8EE252A49'
        batch = {UdlStatsConstants.BATCH_GUID: batch_guid, UdlStatsConstants.TENANT: self.__tenant,
                 UdlStatsConstants.SCHEMA_NAME: batch_guid, Constants.DEACTIVATE: False}
        rtn = cleanup_batch(batch)
        self.assertFalse(rtn)

    def test_cleanup_batch_stureg(self):
        batch_guid = '2bb942b9-75cf-4055-a67a-8b9ab53a9dfc'
        batch = {UdlStatsConstants.BATCH_GUID: batch_guid, UdlStatsConstants.TENANT: self.__tenant,
                 UdlStatsConstants.SCHEMA_NAME: batch_guid, Constants.DEACTIVATE: False}
        rtn = cleanup_batch(batch)
        self.assertFalse(rtn)

    def test_migrate_batch_with_roll_back(self):
        batch = {UdlStatsConstants.REC_ID: '7',
                 UdlStatsConstants.BATCH_GUID: '13DCC2AB-4FC6-418D-844E-65ED5D9CED38',
                 UdlStatsConstants.TENANT: 'tomcat', UdlStatsConstants.SCHEMA_NAME: None,
                 Constants.DEACTIVATE: False, UdlStatsConstants.LOAD_TYPE: LoadType.ASSESSMENT,
                 UdlStatsConstants.BATCH_OPERATION: None,
                 UdlStatsConstants.SNAPSHOT_CRITERIA: None}
        prod_conn = EdMigrateDestConnection(tenant=get_unittest_prod_tenant_name())
        fact_asmt_outcome_table = prod_conn.get_table(Constants.FACT_ASMT_OUTCOME)
        query = select([fact_asmt_outcome_table], fact_asmt_outcome_table.c.asmt_outcome_vw_rec_id.in_([1000000777, 1000000778, 1000001035]))
        query_c = query.where(fact_asmt_outcome_table.c.rec_status == 'C')
        query_d = query.where(fact_asmt_outcome_table.c.rec_status == 'D')
        rset = prod_conn.execute(query_c)
        rows = rset.fetchall()
        row_cnt = len(rows)
        self.assertEqual(3, row_cnt)
        rset.close()
        rset = prod_conn.execute(query_d)
        rows = rset.fetchall()
        row_cnt = len(rows)
        self.assertEqual(0, row_cnt)
        rtn = migrate_batch(batch)
        rset.close()
        self.assertFalse(rtn)
        rset = prod_conn.execute(query_c)
        rows = rset.fetchall()
        row_cnt = len(rows)
        self.assertEqual(3, row_cnt)
        rset.close()
        rset = prod_conn.execute(query_d)
        rows = rset.fetchall()
        row_cnt = len(rows)
        self.assertEqual(0, row_cnt)
        rtn = migrate_batch(batch)
        rset.close()

    def test_report_udl_stats_batch_status(self):
        batches_to_migrate = get_batches_to_migrate('hotdog')
        self.assertEqual(1, len(batches_to_migrate))
        self.assertEqual(UdlStatsConstants.UDL_STATUS_INGESTED, batches_to_migrate[0][UdlStatsConstants.LOAD_STATUS])
        updated_count = report_udl_stats_batch_status(batches_to_migrate[0][UdlStatsConstants.REC_ID], UdlStatsConstants.MIGRATE_INGESTED)
        self.assertEqual(1, updated_count)
        batches_to_migrate = get_batches_to_migrate('hotdog')
        self.assertEqual(0, len(batches_to_migrate))

    def test_report_udl_stats_batch_status_non_exist_batch_id(self):
        self.assertRaises(EdMigrateUdl_statException, report_udl_stats_batch_status, 'non-exist-uuid', UdlStatsConstants.MIGRATE_IN_PROCESS)
