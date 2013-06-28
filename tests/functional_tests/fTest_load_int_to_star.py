import unittest
import csv
from udl2.defaults import UDL2_DEFAULT_CONFIG_PATH_FILE
from udl2 import database
from udl2_util.database_util import connect_db, execute_queries
import imp
from move_to_target import column_mapping, move_to_target 
from udl2 import W_load_from_integration_to_star

class IntToStarFTest(unittest.TestCase):

    def setUp(self):
        try:
            config_path = dict(os.environ)['UDL2_CONF']
        except Exception:
            config_path = UDL2_DEFAULT_CONFIG_PATH_FILE
        udl2_conf = imp.load_source('udl2_conf', config_path)
        from udl2_conf import udl2_conf
        self.udl2_conf = udl2_conf
        self.udl2_conn, self.udl2_engine = database._create_conn_engine(self.udl2_conf['udl2_db'])
        self.target_conn, self.target_engine = database._create_conn_engine(self.udl2_conf['target_db'])

        self.truncate_edware_tables()
        self.truncate_integration_tables()

    def truncate_edware_tables(self):
        template = """
            TRUNCATE "{target_schema}"."{target_table}" CASCADE
            """

        sql_dim_asmt = template.format(target_schema=self.udl2_conf['target_db']['db_schema'],target_table='dim_asmt')
        sql_dim_inst_hier = template.format(target_schema=self.udl2_conf['target_db']['db_schema'],target_table='dim_inst_hier')
        sql_dim_section = template.format(target_schema=self.udl2_conf['target_db']['db_schema'],target_table='dim_section')
        sql_dim_staff = template.format(target_schema=self.udl2_conf['target_db']['db_schema'],target_table='dim_staff')
        sql_dim_student = template.format(target_schema=self.udl2_conf['target_db']['db_schema'],target_table='dim_student')
        sql_fact_asmt_outcome = template.format(target_schema=self.udl2_conf['target_db']['db_schema'],target_table='fact_asmt_outcome')

        except_msg = "Unable to clean up target db tabels"
        execute_queries(self.target_conn, [sql_dim_asmt, sql_dim_inst_hier, sql_dim_section, sql_dim_staff, sql_dim_student, sql_fact_asmt_outcome], except_msg)

    def truncate_integration_tables(self):
        sql_template = """
            TRUNCATE "{staging_schema}"."{staging_table}" CASCADE
            """
        sql_int_asmt = sql_template.format(staging_schema=self.udl2_conf['udl2_db']['integration_schema'],
                                  staging_table='INT_SBAC_ASMT') 
        sql_int_asmt_outcome = sql_template.format(staging_schema=self.udl2_conf['udl2_db']['integration_schema'],
                                  staging_table='INT_SBAC_ASMT_OUTCOME') 

        except_msg = "Unable to clean up integration tables"
        execute_queries(self.udl2_conn, [sql_int_asmt, sql_int_asmt_outcome], except_msg)

    def test_load_int_to_star(self):
        
        table = 'INT_SBAC_ASMT'
        insert_sql = """INSERT INTO "{staging_schema}"."{staging_table}" VALUES({value_string});"""
        insert_array = []
        with open('../data/INT_SBAC_ASMT.csv') as f:
            cf = csv.reader(f, delimiter=',', quoting=csv.QUOTE_ALL)
            next(cf) 
            for row in cf:
                values = '"'+'", "'.join(row)+'"'
                values = """'4', \'"""+"""', '""".join(row)+"""'"""
                values = values.replace('""','"0"')
                values = values.replace("''","'0'")
                values = values.replace ("'DEFAULT'","DEFAULT")
                insert_string = insert_sql.format(staging_schema=self.udl2_conf['udl2_db']['integration_schema'],staging_table=table,value_string=values)
                insert_array.append(insert_string)
            except_msg = "Unable to insert into %s" % table
            execute_queries(self.udl2_conn, insert_array, except_msg)

        table = 'INT_SBAC_ASMT_OUTCOME'
        insert_array=[]
        with open('../data/INT_SBAC_ASMT_OUTCOME.csv') as f:
            cf = csv.reader(f, delimiter=',', quoting=csv.QUOTE_ALL)
            next(cf) 
            for row in cf:
                values = '"'+'", "'.join(row)+'"'
                values = """DEFAULT, \'"""+"""', '""".join(row)+"""'"""
                values = values.replace('""','"0"')
                values = values.replace("''","'0'")
                values = values.replace ("'DEFAULT'","DEFAULT")
                insert_string = insert_sql.format(staging_schema=self.udl2_conf['udl2_db']['integration_schema'],staging_table=table,value_string=values)
                insert_array.append(insert_string)
            except_msg = "Unable to insert into %s" % table
            execute_queries(self.udl2_conn, insert_array, except_msg)

        #explode to dim tables
        dim_tables = column_mapping.get_target_tables_parallel()
        column_map = column_mapping.get_column_mapping()
        batch_id = 'c721c7de-48b7-4c05-85bd-3ff360b6e844'
        conf = W_load_from_integration_to_star.generate_conf(batch_id)

        for target in dim_tables.keys():
            target_columns = column_map[target]
            column_types = move_to_target.get_table_column_types(conf,target,list(target_columns.keys()))
            move_to_target.explode_data_to_dim_table(conf, dim_tables[target], target, target_columns, column_types)

        column_types = move_to_target.get_table_column_types(conf,'fact_asmt_outcome',list(column_map['fact_asmt_outcome'].keys()))
        move_to_target.explode_data_to_fact_table(conf, 'INT_SBAC_ASMT_OUTCOME', 'fact_asmt_outcome', column_map['fact_asmt_outcome'], column_types)

        count_template = """ SELECT COUNT(*) FROM "{schema}"."{table}" """
        tables_to_check = {'dim_asmt':1,'dim_inst_hier':206,'dim_staff':206,'dim_student':9997,'fact_asmt_outcome':19793}
        
        for entry in tables_to_check.keys():
            sql = count_template.format(schema=self.udl2_conf['target_db']['db_schema'],table=entry)
            result = self.target_conn.execute(sql)
            count = 0
            for row in result:
                count = row[0]
            assert int(count) == tables_to_check[entry]
