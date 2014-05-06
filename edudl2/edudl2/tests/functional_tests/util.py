import os
import unittest
from edudl2.udl2.defaults import UDL2_DEFAULT_CONFIG_PATH_FILE
from edudl2.udl2_util.config_reader import read_ini_file
from edudl2.database.udl2_connector import initialize_db_target,\
    initialize_db_udl, initialize_db_prod, get_target_connection,\
    get_udl_connection
from sqlalchemy.sql.expression import select, func, true, cast
from sqlalchemy.types import Integer
from edcore.database.utils.utils import create_schema, drop_schema
from edschema.metadata.ed_metadata import generate_ed_metadata
from edschema.metadata.util import get_tables_starting_with


class UDLTestHelper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config_path = dict(os.environ).get('UDL2_CONF', UDL2_DEFAULT_CONFIG_PATH_FILE)
        conf_tup = read_ini_file(config_path)
        cls.udl2_conf = conf_tup[0]
        initialize_db_udl(cls.udl2_conf)
        initialize_db_target(cls.udl2_conf)
        initialize_db_prod(cls.udl2_conf)
        cls.truncate_edware_tables()
        cls.truncate_udl_tables()

    @classmethod
    def tearDownClass(cls):
        cls.truncate_edware_tables()
        cls.truncate_udl_tables()

    @classmethod
    def truncate_edware_tables(self, tenant='cat'):
        with get_target_connection(tenant, schema_name='edware') as conn:
            metadata = conn.get_metadata()
            for table in reversed(metadata.sorted_tables):
                conn.execute(table.delete())

    @classmethod
    def truncate_udl_tables(self):
        with get_udl_connection() as conn:
            tables = get_tables_starting_with(conn.get_metadata(), 'int_') + \
                get_tables_starting_with(conn.get_metadata(), 'stg_') + ['err_list', 'udl_batch']
            for t in tables:
                table = conn.get_table(t)
                conn.execute(table.delete())

    @classmethod
    def create_schema_for_target(cls, tenant, guid_batch):
        with get_target_connection(tenant) as connector:
            create_schema(connector, generate_ed_metadata, guid_batch)

    @classmethod
    def drop_target_schema(cls, tenant, guid_batch):
        with get_target_connection(tenant) as connector:
            drop_schema(connector, guid_batch)

    def get_staging_asmt_score_avgs(self):
        with get_udl_connection() as conn:
            stg_outcome = conn.get_table('stg_sbac_asmt_outcome')
            query = select([func.avg(cast(stg_outcome.c.score_asmt, Integer)),
                            func.avg(cast(stg_outcome.c.score_asmt_min, Integer)),
                            func.avg(cast(stg_outcome.c.score_asmt_max, Integer)),
                            func.avg(cast(stg_outcome.c.score_claim_1, Integer)),
                            func.avg(cast(stg_outcome.c.score_claim_1_min, Integer)),
                            func.avg(cast(stg_outcome.c.score_claim_1_max, Integer)),
                            func.avg(cast(stg_outcome.c.score_claim_2, Integer)),
                            func.avg(cast(stg_outcome.c.score_claim_2_min, Integer)),
                            func.avg(cast(stg_outcome.c.score_claim_2_max, Integer)),
                            func.avg(cast(stg_outcome.c.score_claim_3, Integer)),
                            func.avg(cast(stg_outcome.c.score_claim_3_min, Integer)),
                            func.avg(cast(stg_outcome.c.score_claim_3_max, Integer)),
                            func.avg(cast(stg_outcome.c.score_claim_4, Integer)),
                            func.avg(cast(stg_outcome.c.score_claim_4_min, Integer)),
                            func.avg(cast(stg_outcome.c.score_claim_4_max, Integer))], from_obj=stg_outcome)
            result = conn.execute(query)
            for row in result:
                asmt_avgs = row

            return asmt_avgs

    def get_integration_asmt_score_avgs(self):
        with get_udl_connection() as conn:
            int_outcome = conn.get_table('int_sbac_asmt_outcome')
            query = select([func.avg(int_outcome.c.score_asmt),
                            func.avg(int_outcome.c.score_asmt_min),
                            func.avg(int_outcome.c.score_asmt_max),
                            func.avg(int_outcome.c.score_claim_1),
                            func.avg(int_outcome.c.score_claim_1_min),
                            func.avg(int_outcome.c.score_claim_1_max),
                            func.avg(int_outcome.c.score_claim_2),
                            func.avg(int_outcome.c.score_claim_2_min),
                            func.avg(int_outcome.c.score_claim_2_max),
                            func.avg(int_outcome.c.score_claim_3),
                            func.avg(int_outcome.c.score_claim_3_min),
                            func.avg(int_outcome.c.score_claim_3_max),
                            func.avg(int_outcome.c.score_claim_4),
                            func.avg(int_outcome.c.score_claim_4_min),
                            func.avg(int_outcome.c.score_claim_4_max)], from_obj=int_outcome)
            result = conn.execute(query)
            for row in result:
                asmt_avgs = row

            return asmt_avgs

    def get_edware_asmt_score_avgs(self, tenant, schema):
        with get_target_connection(tenant, schema) as conn:
            fact = conn.get_table('fact_asmt_outcome')
            query = select([func.avg(fact.c.asmt_score),
                            func.avg(fact.c.asmt_score_range_min),
                            func.avg(fact.c.asmt_score_range_max),
                            func.avg(fact.c.asmt_claim_1_score),
                            func.avg(fact.c.asmt_claim_1_score_range_min),
                            func.avg(fact.c.asmt_claim_1_score_range_max),
                            func.avg(fact.c.asmt_claim_2_score),
                            func.avg(fact.c.asmt_claim_2_score_range_min),
                            func.avg(fact.c.asmt_claim_2_score_range_max),
                            func.avg(fact.c.asmt_claim_3_score),
                            func.avg(fact.c.asmt_claim_3_score_range_min),
                            func.avg(fact.c.asmt_claim_3_score_range_max),
                            func.avg(fact.c.asmt_claim_4_score),
                            func.avg(fact.c.asmt_claim_4_score_range_min),
                            func.avg(fact.c.asmt_claim_4_score_range_max)], from_obj=fact)
            result = conn.execute(query)
            for row in result:
                star_asmt_avgs = row

            return star_asmt_avgs

    def get_staging_demographic_counts(self):
        demographics = ['dmg_eth_hsp', 'dmg_eth_ami', 'dmg_eth_asn', 'dmg_eth_blk', 'dmg_eth_pcf', 'dmg_eth_wht', 'dmg_prg_iep', 'dmg_prg_lep', 'dmg_prg_504', 'dmg_prg_tt1']
        results_dict = {}
        with get_udl_connection() as conn:
            stg_outcome = conn.get_table('stg_sbac_asmt_outcome')
            for entry in demographics:
                query = select([func.count(stg_outcome.c[entry])], from_obj=stg_outcome).where(stg_outcome.c[entry].in_(['Y', 'y', 'yes']))
                result = conn.execute(query)
                for row in result:
                    demo_count = row[0]

                results_dict[entry] = demo_count

        return results_dict

    def get_integration_demographic_counts(self):
        demographics = ['dmg_eth_hsp', 'dmg_eth_ami', 'dmg_eth_asn', 'dmg_eth_blk', 'dmg_eth_pcf', 'dmg_eth_wht', 'dmg_prg_iep', 'dmg_prg_lep', 'dmg_prg_504', 'dmg_prg_tt1']
        results_dict = {}
        with get_udl_connection() as conn:
            int_outcome = conn.get_table('int_sbac_asmt_outcome')
            for entry in demographics:
                query = select([func.count(int_outcome.c[entry])], from_obj=int_outcome).where(int_outcome.c[entry] == true())
                result = conn.execute(query)
                for row in result:
                    demo_count = row[0]

                results_dict[entry] = demo_count

            #get derived ethnicity
            eth_query = select([func.count(int_outcome.c[entry])], from_obj=int_outcome).where(int_outcome.c[entry] is not None)
            result = conn.execute(eth_query)
            for row in result:
                derived_count = row[0]
            results_dict['dmg_eth_derived'] = derived_count

        return results_dict

    def get_star_schema_demographic_counts(self, tenant, schema):
        demographics = ['dmg_eth_hsp', 'dmg_eth_ami', 'dmg_eth_asn', 'dmg_eth_blk', 'dmg_eth_pcf', 'dmg_eth_wht', 'dmg_prg_iep', 'dmg_prg_lep', 'dmg_prg_504', 'dmg_prg_tt1']
        results_dict = {}
        with get_target_connection(tenant, schema) as conn:
            fact = conn.get_table('fact_asmt_outcome')
            for entry in demographics:
                demo_query = select([func.count(fact.c[entry])], from_obj=fact).where(fact.c[entry] == true())
                result = conn.execute(demo_query)
                for row in result:
                    demo_count = row[0]

                results_dict[entry] = demo_count

                #get derived ethnicity
                eth_query = select([func.count(fact.c.dmg_eth_derived)], from_obj=fact).where(fact.c.dmg_eth_derived is not None)
                result = conn.execute(eth_query)
                for row in result:
                    derived_count = row[0]
                results_dict['dmg_eth_derived'] = derived_count

        return results_dict
