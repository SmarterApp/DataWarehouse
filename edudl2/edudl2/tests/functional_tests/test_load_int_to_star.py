import csv
import os
from edudl2.udl2_util.database_util import execute_queries
from edudl2.move_to_target import move_to_target, move_to_target_setup
from edudl2.tests.functional_tests.util import UDLTestHelper
from sqlalchemy.sql.expression import text, bindparam
from edudl2.exceptions.udl_exceptions import DeleteRecordNotFound
from unittest import skip


class IntToStarFTest(UDLTestHelper):

    @classmethod
    def setUpClass(cls):
        super(IntToStarFTest, cls).setUpClass()

    def setUp(self):
        super(IntToStarFTest, self).setUp()
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.guid_batch = '2411183a-dfb7-42f7-9b3e-bb7a597aa3e7'
        self.phase_number = 4
        self.load_type = 'assessment'
        self.tenant_code = 'edware'
        self.conf = move_to_target_setup.generate_conf(self.guid_batch, self.phase_number,
                                                       self.load_type, self.tenant_code)
        self.match_conf = move_to_target_setup.get_move_to_target_conf()['handle_deletions']
        self.load_to_dim_task_name = "udl2.W_load_from_integration_to_star.explode_data_to_dim_table_task"
        self.load_to_fact_task_name = "udl2.W_load_from_integration_to_star.explode_data_to_fact"
        self.dim_table_prefix = 'dim_'
        self.fact_table_prefix = 'fact_'
        self.insert_sql = 'INSERT INTO "{staging_schema}"."{staging_table}" ({columns_string}) VALUES ({value_string});'
        self.count_sql = ' SELECT COUNT(*) FROM "{schema}"."{table}" '
        self.matched_prod_values = [{}, {}]

    def tearDown(self):
        super(IntToStarFTest, self).tearDown()

    def generate_insert_items(self, header, row):
        row = [r if str(r) != '' else '0' for r in row]
        columns_values = dict(zip(header, row))
        columns = [k for k, v in columns_values.items()]
        values = [":{k}".format(k=k) for k, v in columns_values.items()]
        params = [bindparam(k, v) for k, v in columns_values.items()]
        return (columns, values, params)

    def load_int_sbac_asmt(self):
        table = 'INT_SBAC_ASMT'
        insert_array = []
        with open(os.path.join(self.data_dir, 'INT_SBAC_ASMT.csv')) as f:
            cf = csv.reader(f, delimiter=',', quoting=csv.QUOTE_ALL)
            header = next(cf)
            header.insert(0, 'record_sid')
            for row in cf:
                # set record_sid = 7 in this func test
                row.insert(0, str(7))
                (columns, values, params) = self.generate_insert_items(header, row)
                insert_query = text(self.insert_sql.format(staging_schema=self.udl2_conf['udl2_db']['integration_schema'],
                                                           staging_table=table,
                                                           columns_string=", ".join(columns),
                                                           value_string=", ".join(values)),
                                    bindparams=params)
                insert_array.append(insert_query)
            except_msg = "Unable to insert into %s" % table
            execute_queries(self.udl2_conn, insert_array, except_msg)

    def load_int_sbac_asmt_outcome(self):
        table = 'INT_SBAC_ASMT_OUTCOME'
        insert_array = []
        with open(os.path.join(self.data_dir, 'INT_SBAC_ASMT_OUTCOME.csv')) as f:
            cf = csv.reader(f, delimiter=',', quoting=csv.QUOTE_ALL)
            header = next(cf)
            for row in cf:
                (columns, values, params) = self.generate_insert_items(header, row)
                insert_query = text(self.insert_sql.format(staging_schema=self.udl2_conf['udl2_db']['integration_schema'],
                                                           staging_table=table,
                                                           columns_string=", ".join(columns),
                                                           value_string=", ".join(values)),
                                    bindparams=params)
                insert_array.append(insert_query)
            except_msg = "Unable to insert into %s" % table
            execute_queries(self.udl2_conn, insert_array, except_msg)

    def add_delete_prod_record(self):
        pass

    def remove_delete_prod_record(self):
        pass

    def test_1_load_int_to_star(self):
        self.load_int_sbac_asmt()
        self.load_int_sbac_asmt_outcome()

        # explode to dim tables

        table_map, column_map = move_to_target_setup.get_table_and_column_mapping(self.conf,
                                                                                  self.load_to_dim_task_name,
                                                                                  self.dim_table_prefix)
        for target in table_map.keys():
            target_columns = column_map[target]
            column_types = move_to_target_setup.get_table_column_types(self.conf, target, list(target_columns.keys()))
            move_to_target.explode_data_to_dim_table(self.conf, table_map[target], target, target_columns, column_types)
        # explode to fact table
        table_map, column_map = move_to_target_setup.get_table_and_column_mapping(self.conf,
                                                                                  self.load_to_fact_task_name,
                                                                                  self.fact_table_prefix)
        column_types = move_to_target_setup.get_table_column_types(self.conf,
                                                                   list(table_map.keys())[0],
                                                                   list(column_map['fact_asmt_outcome'].keys()))
        move_to_target.explode_data_to_fact_table(self.conf,
                                                  list(table_map.values())[0],
                                                  list(table_map.keys())[0],
                                                  column_map['fact_asmt_outcome'],
                                                  column_types)

        # handle deletion case
        matched_results = move_to_target.match_deleted_records(self.conf, self.match_conf)
        move_to_target.update_deleted_record_rec_id(self.conf, self.match_conf, matched_results)
        move_to_target.check_mismatched_deletions(self.conf, self.match_conf)

        # check star schema table counts
        tables_to_check = {'dim_asmt': 1, 'dim_inst_hier': 71, 'dim_student': 94, 'fact_asmt_outcome': 99}
        for entry in tables_to_check.keys():
            query = text(self.count_sql.format(schema=self.udl2_conf['target_db']['db_schema'],
                                               table=entry))
            result = self.target_conn.execute(query)
            self.assertEqual(int(result.fetchall()[0][0]), tables_to_check[entry])

        # check asmt score avgs
        int_asmt_avgs = self.get_integration_asmt_score_avgs()
        star_asmt_avgs = self.get_edware_asmt_score_avgs()

        self.assertEqual(int_asmt_avgs, star_asmt_avgs)

        # check demographic counts
        int_demo_dict = self.get_integration_demographic_counts()
        star_demo_dict = self.get_star_schema_demographic_counts()

        self.assertEqual(int_demo_dict, star_demo_dict)

    @skip('In development')
    def test_2_match_deleted_records(self):
        query = text(self.count_sql.format(schema=self.udl2_conf['target_db']['db_schema'],
                                           table='fact_asmt_outcome'))
        result = self.target_conn.execute(query)
        print(result.fetchall()[0][0])
        matched_prod_values = move_to_target.match_deleted_records(self.conf, self.match_conf)
        self.assertListEqual(self.matched_prod_values, matched_prod_values)

    @skip('In development')
    def test_3_update_deleted_record_rec_id(self):
        query = text(self.count_sql.format(schema=self.udl2_conf['target_db']['db_schema'],
                                           table='fact_asmt_outcome'))
        result = self.target_conn.execute(query)
        print(result.fetchall()[0][0])
        result = move_to_target.update_deleted_record_rec_id(self.conf, self.match_conf, self.matched_prod_values)
        self.assertIsNotNone(result)

    @skip('In development')
    def test_4_check_mismatched_deletions(self):
        query = text(self.count_sql.format(schema=self.udl2_conf['target_db']['db_schema'],
                                           table='fact_asmt_outcome'))
        result = self.target_conn.execute(query)
        print(result.fetchall()[0][0])
        # first there should be no exception, so it just return None
        result = move_to_target.check_mismatched_deletions(self.conf, self.match_conf)
        self.assertIsNotNone(result)

    @skip('In development')
    def test_5_check_mismatched_deletions_2(self):
        query = text(self.count_sql.format(schema=self.udl2_conf['target_db']['db_schema'],
                                           table='fact_asmt_outcome'))
        result = self.target_conn.execute(query)
        print(result.fetchall()[0][0])
        # now add one more row on the fact_asmt_outcome, this should trigger exception
        # add code that insert one more row
        self.assertRaises(DeleteRecordNotFound, move_to_target.check_mismatched_deletions(self.conf, self.match_conf))
