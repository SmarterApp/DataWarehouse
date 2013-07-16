import os
import unittest
import move_to_target.column_mapping as col_mapping
import move_to_target.create_queries as queries
from move_to_target import move_to_target
from udl2.defaults import UDL2_DEFAULT_CONFIG_PATH_FILE
import imp
from collections import OrderedDict
import datetime
from udl2 import message_keys as mk


class TestMoveToTarget(unittest.TestCase):

    def setUp(self,):
        try:
            config_path = dict(os.environ)['UDL2_CONF']
        except Exception:
            config_path = UDL2_DEFAULT_CONFIG_PATH_FILE
        udl2_conf = imp.load_source('udl2_conf', config_path)
        from udl2_conf import udl2_conf
        self.conf = udl2_conf

    def tearDown(self,):
        pass

    def test_create_queries_for_move_to_fact_table(self):
        guid_batch = '8866c6d5-7e5e-4c54-bf4e-775abc4021b2'
        conf = generate_conf(guid_batch, self.conf)
        source_table = col_mapping.get_target_table_callback()[1]
        target_table = col_mapping.get_target_table_callback()[0]
        column_mapping = col_mapping.get_column_mapping()[target_table]
        # give value for 2 foreign keys
        column_mapping['asmt_rec_id'] = '100'
        column_mapping['section_rec_id'] = '1'
        column_types = get_expected_column_types_for_fact_table(target_table)

        expected_query_1 = 'ALTER TABLE \"edware\".\"{target_table}\" DISABLE TRIGGER ALL'.format(target_table=target_table)
        expected_query_2 = get_expected_insert_query_for_fact_table(target_table, column_mapping['asmt_rec_id'], column_mapping['section_rec_id'], guid_batch,
                                                                    conf[mk.SOURCE_DB_NAME], conf[mk.SOURCE_DB_USER], conf[mk.SOURCE_DB_PASSWORD])
        expected_query_3 = get_expected_update_inst_hier_rec_id_query(target_table)
        expected_query_4 = 'ALTER TABLE \"edware\".\"{target_table}\" ENABLE TRIGGER ALL'.format(target_table=target_table)
        expected_value = [expected_query_1, expected_query_2, expected_query_3, expected_query_4]
        actual_value = move_to_target.create_queries_for_move_to_fact_table(conf, source_table, target_table, column_mapping, column_types)
        self.maxDiff = None
        self.assertEqual(len(expected_value), len(actual_value))
        for i in range(len(expected_value)):
            print("this is %i", i)
            print("expected == ", expected_value[i].strip())
            print("actual   == ", actual_value[i].strip())
            self.assertEqual(expected_value[i].strip(), actual_value[i].strip())

    def test_create_insert_query_for_dim_table(self):
        guid_batch = '8866c6d5-7e5e-4c54-bf4e-775abc4021b2'
        conf = generate_conf(guid_batch, self.conf)
        target_table, source_table = list(col_mapping.get_target_tables_parallel().items())[0]
        column_mapping = col_mapping.get_column_mapping()[target_table]
        column_types = get_expected_column_types_for_dim_inst_hier(target_table)
        actual_value = queries.create_insert_query(conf, source_table, target_table, column_mapping, column_types, True)
        expected_value = get_expected_insert_query_for_dim_inst_hier(target_table, guid_batch, conf[mk.SOURCE_DB_NAME], conf[mk.SOURCE_DB_USER], conf[mk.SOURCE_DB_PASSWORD])
        self.assertEqual(expected_value, actual_value)

    def test_calculate_spend_time_as_second(self):
        start_time = datetime.datetime(2013, 5, 10, 16, 34, 33)
        finish_time = datetime.datetime(2013, 5, 10, 16, 40, 0)
        expected_value = 327.0
        actual_value = move_to_target.calculate_spend_time_as_second(start_time, finish_time)
        self.assertEqual(expected_value, actual_value)


def generate_conf(guid_batch, udl2_conf):
    '''
    Return all needed configuration information
    '''
    conf = {
            # add guid_batch from msg
            mk.GUID_BATCH: guid_batch,

            # source schema
            mk.SOURCE_DB_SCHEMA: udl2_conf['udl2_db']['integration_schema'],
            # source database setting
            mk.SOURCE_DB_HOST: udl2_conf['udl2_db']['db_host'],
            mk.SOURCE_DB_PORT: udl2_conf['udl2_db']['db_port'],
            mk.SOURCE_DB_USER: udl2_conf['udl2_db']['db_user'],
            mk.SOURCE_DB_NAME: udl2_conf['udl2_db']['db_database'],
            mk.SOURCE_DB_PASSWORD: udl2_conf['udl2_db']['db_pass'],

            # target schema
            mk.TARGET_DB_SCHEMA: udl2_conf['target_db']['db_schema'],
            # target database setting
            mk.TARGET_DB_HOST: udl2_conf['target_db']['db_host'],
            mk.TARGET_DB_PORT: udl2_conf['target_db']['db_port'],
            mk.TARGET_DB_USER: udl2_conf['target_db']['db_user'],
            mk.TARGET_DB_NAME: udl2_conf['target_db']['db_database'],
            mk.TARGET_DB_PASSWORD: udl2_conf['target_db']['db_pass'],
    }
    return conf


def get_expected_column_types_for_fact_table(table_name):
    column_names = list(col_mapping.get_column_mapping()[table_name].keys())
    column_types = ['asmnt_outcome_rec_id bigint', 'asmt_rec_id bigint', 'student_guid character varying(50)',
                    'teacher_guid character varying(50)', 'state_code character varying(2)', 'district_guid character varying(50)',
                    'school_guid character varying(50)', 'section_guid character varying(50)', 'inst_hier_rec_id bigint',
                    'section_rec_id bigint', 'where_taken_id character varying(50)', 'where_taken_name character varying(256)',
                    'asmt_grade character varying(10)', 'enrl_grade character varying(10)', 'date_taken character varying(8)',
                    'date_taken_day smallint', 'date_taken_month smallint', 'date_taken_year smallint', 'asmt_score smallint',
                    'asmt_score_range_min smallint', 'asmt_score_range_max smallint', 'asmt_perf_lvl smallint',
                    'asmt_claim_1_score smallint', 'asmt_claim_1_score_range_min smallint', 'asmt_claim_1_score_range_max smallint',
                    'asmt_claim_2_score smallint', 'asmt_claim_2_score_range_min smallint', 'asmt_claim_2_score_range_max smallint',
                    'asmt_claim_3_score smallint', 'asmt_claim_3_score_range_min smallint', 'asmt_claim_3_score_range_max smallint',
                    'asmt_claim_4_score smallint', 'asmt_claim_4_score_range_min smallint', 'asmt_claim_4_score_range_max smallint',
                    'record_create_datetime timestamp without time zone', 'status character varying(2)', 'most_recent boolean', 'batch_guid character varying(50)']
    column_name_type_map = OrderedDict()
    for i in range(len(column_names)):
        column_name_type_map[column_names[i]] = column_types[i]
    return column_name_type_map


def get_expected_insert_query_for_fact_table(table_name, asmt_rec_id, section_rec_id, guid_batch, dbname, user, password):
    return 'INSERT INTO "edware"."{table_name}"(asmnt_outcome_rec_id,asmt_rec_id,student_guid,teacher_guid,state_code,district_guid,'\
            'school_guid,section_guid,inst_hier_rec_id,section_rec_id,where_taken_id,where_taken_name,asmt_grade,enrl_grade,date_taken,'\
            'date_taken_day,date_taken_month,date_taken_year,asmt_score,asmt_score_range_min,asmt_score_range_max,asmt_perf_lvl,'\
            'asmt_claim_1_score,asmt_claim_1_score_range_min,asmt_claim_1_score_range_max,asmt_claim_2_score,asmt_claim_2_score_range_min,'\
            'asmt_claim_2_score_range_max,asmt_claim_3_score,asmt_claim_3_score_range_min,asmt_claim_3_score_range_max,asmt_claim_4_score,'\
            'asmt_claim_4_score_range_min,asmt_claim_4_score_range_max,record_create_datetime,status,most_recent,batch_guid) '\
            ' SELECT * FROM dblink(\'dbname={dbname} user={user} password={password}\', \'SELECT nextval(\'\'"GLOBAL_REC_SEQ"\'\'), * FROM '\
            '(SELECT {asmt_rec_id},guid_student,guid_staff,code_state,guid_district,guid_school,\'\' \'\',-1,{section_rec_id},guid_asmt_location,name_asmt_location,grade_asmt,'\
            'grade_enrolled,date_assessed,date_taken_day,date_taken_month,date_taken_year,score_asmt,score_asmt_min,score_asmt_max,score_perf_level,'\
            'score_claim_1,score_claim_1_min,score_claim_1_max,score_claim_2,score_claim_2_min,score_claim_2_max,score_claim_3,score_claim_3_min,score_claim_3_max,'\
            'score_claim_4,score_claim_4_min,score_claim_4_max,CURRENT_TIMESTAMP,\'\' \'\',True,guid_batch '\
            'FROM "udl2"."INT_SBAC_ASMT_OUTCOME" WHERE guid_batch=\'\'{guid_batch}\'\') as y\') AS t(asmnt_outcome_rec_id bigint,asmt_rec_id bigint,student_guid character varying(50),'\
            'teacher_guid character varying(50),state_code character varying(2),district_guid character varying(50),school_guid character varying(50),'\
            'section_guid character varying(50),inst_hier_rec_id bigint,section_rec_id bigint,where_taken_id character varying(50),where_taken_name character varying(256),'\
            'asmt_grade character varying(10),enrl_grade character varying(10),date_taken character varying(8),date_taken_day smallint,date_taken_month smallint,'\
            'date_taken_year smallint,asmt_score smallint,asmt_score_range_min smallint,asmt_score_range_max smallint,asmt_perf_lvl smallint,asmt_claim_1_score smallint,'\
            'asmt_claim_1_score_range_min smallint,asmt_claim_1_score_range_max smallint,asmt_claim_2_score smallint,asmt_claim_2_score_range_min smallint,'\
            'asmt_claim_2_score_range_max smallint,asmt_claim_3_score smallint,asmt_claim_3_score_range_min smallint,asmt_claim_3_score_range_max smallint,'\
            'asmt_claim_4_score smallint,asmt_claim_4_score_range_min smallint,asmt_claim_4_score_range_max smallint,record_create_datetime timestamp without time zone,'\
            'status character varying(2),most_recent boolean,batch_guid character varying(50));'.format(table_name=table_name, asmt_rec_id=asmt_rec_id, section_rec_id=section_rec_id, guid_batch=guid_batch,
                                                                                                        dbname=dbname, user=user, password=password)


def get_expected_update_inst_hier_rec_id_query(table_name):
    return 'UPDATE "edware"."{table_name}" SET inst_hier_rec_id=dim.dim_inst_hier_rec_id FROM '\
    '(SELECT inst_hier_rec_id AS dim_inst_hier_rec_id, state_code AS dim_state_code,district_guid AS dim_district_guid,school_guid AS dim_school_guid '\
    'FROM "edware"."dim_inst_hier")dim WHERE inst_hier_rec_id=-1 AND state_code=dim_state_code AND '\
    'district_guid=dim_district_guid AND school_guid=dim_school_guid'.format(table_name=table_name)


def get_expected_column_types_for_dim_inst_hier(table_name):
    column_names = list(col_mapping.get_column_mapping()[table_name].keys())
    column_types = ['inst_hier_rec_id bigint', 'state_name character varying(32)', 'state_code character varying(2)', 'district_guid character varying(50)',
                    'district_name character varying(256)', 'school_guid character varying(50)', 'school_name character varying(256)',
                    'school_category character varying(20)', 'from_date character varying(8)', 'to_date character varying(8)', 'most_recent boolean']
    column_name_type_map = OrderedDict()
    for i in range(len(column_names)):
        column_name_type_map[column_names[i]] = column_types[i]
    return column_name_type_map


def get_expected_insert_query_for_dim_inst_hier(table_name, guid_batch, dbname, user, password):
    return 'INSERT INTO \"edware\"."{table_name}"(inst_hier_rec_id,state_name,state_code,district_guid,district_name,'\
           'school_guid,school_name,school_category,from_date,to_date,most_recent)  SELECT * FROM '\
           'dblink(\'dbname={dbname} user={user} password={password}\', \'SELECT nextval(\'\'"GLOBAL_REC_SEQ"\'\'), '\
           '* FROM (SELECT DISTINCT name_state,code_state,guid_district,name_district,guid_school,name_school,type_school,'\
           'to_char(CURRENT_TIMESTAMP, \'\'yyyymmdd\'\'),\'\'99991231\'\',True FROM "udl2"."INT_SBAC_ASMT_OUTCOME" WHERE guid_batch=\'\'{guid_batch}\'\') as y\') '\
           'AS t(inst_hier_rec_id bigint,state_name character varying(32),state_code character varying(2),district_guid character varying(50),'\
           'district_name character varying(256),school_guid character varying(50),school_name character varying(256),'\
           'school_category character varying(20),from_date character varying(8),to_date character varying(8),'\
           'most_recent boolean);'.format(table_name=table_name, guid_batch=guid_batch, dbname=dbname, user=user, password=password)


if __name__ == '__main__':
    unittest.main()
