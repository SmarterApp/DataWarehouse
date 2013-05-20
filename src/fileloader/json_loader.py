'''
Created on May 16, 2013

@author: swimberly
'''

import argparse
import json
from sqlalchemy.engine import create_engine

DBDRIVER = "postgresql+pypostgresql"


def load_json(conf):
    ''' Main method for loading json into the integration table '''

    json_dict = read_json_file(conf['json_file'])
    flattened_json = flatten_json_dict(json_dict, conf['mappings'])
    load_to_table(flattened_json, conf['db_host'], conf['db_name'], conf['db_user'], conf['db_port'], conf['db_password'])


def read_json_file(json_file):
    '''
    Read a json file into a dictionary
    @param json_file: The path to the json file to read
    @return: A dictionary containing the data from the json file
    @rtype: dict
    '''

    with open(json_file, 'r') as jf:
        return json.load(jf)


def flatten_json_dict(json_dict, mappings):
    '''
    convert a dictionary into a corresponding flat csv format
    @param json_dict: the dictionary containing the json data
    @param mappings: A dictionary with values indicate the location of the value
    @return: A dictionary of columns mapped to values
    @rtype: dict
    '''

    flat_data = {}
    for key in mappings:
        location_list = mappings[key]
        flat_data[key] = get_nested_data(location_list, json_dict)

    return flat_data


def get_nested_data(location_list, json_dict):
    '''
    Take the location list and the json data and return the value at the end of the search path
    @param location_list: A list containing strings or ints that show the path to the desired data
    @param json_dict: The json data in a dictionary
    @return: the desired value at the end of the path
    '''

    value = json_dict
    for loc_key in location_list:
        value = value[loc_key]

    return value


def load_to_table(data_dict, db_host, db_name, db_user, db_port, db_password):
    ''' Load the table into the proper table '''
    #print(data_dict)
    print(json.dumps(data_dict, indent=4))


def connect_db(user, passwd, host, db_name):
    '''
    Connect to database via sqlalchemy
    '''

    # TODO:define conf_args content
    db_string = DBDRIVER + '://{db_user}:{db_password}@{db_host}/{db_name}'.format(db_user=user, db_password=passwd, db_host=host, db_name=db_name)
    # print(db_string)
    engine = create_engine(db_string)
    db_connection = engine.connect()
    return db_connection, engine


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', dest='source_json', required=True, help="path to the source file")
    args = parser.parse_args()

    mapping = {'asmt_guid': ['identification', 'guid'],
               'asmt_type': ['identification', 'type'],
               'asmt_period': ['identification', 'period'],
               'asmt_period_year': ['identification', 'year'],
               'asmt_version': ['identification', 'version'],
               'asmt_subject': ['identification', 'subject'],
               'asmt_claim_1_name': ['claims', 'claim_1', 'name'],
               'asmt_claim_2_name': ['claims', 'claim_2', 'name'],
               'asmt_claim_3_name': ['claims', 'claim_3', 'name'],
               'asmt_claim_4_name': ['claims', 'claim_4', 'name'],
               'asmt_perf_lvl_name_1': ['performance_levels', 'level_1', 'name'],
               'asmt_perf_lvl_name_2': ['performance_levels', 'level_2', 'name'],
               'asmt_perf_lvl_name_3': ['performance_levels', 'level_3', 'name'],
               'asmt_perf_lvl_name_4': ['performance_levels', 'level_4', 'name'],
               'asmt_perf_lvl_name_5': ['performance_levels', 'level_5', 'name'],
               'asmt_score_min': ['overall', 'min_score'],
               'asmt_score_max': ['overall', 'max_score'],
               'asmt_claim_1_score_min': ['claims', 'claim_1', 'min_score'],
               'asmt_claim_1_score_max': ['claims', 'claim_1', 'max_score'],
               'asmt_claim_1_score_weight': ['claims', 'claim_1', 'weight'],
               'asmt_claim_2_score_min': ['claims', 'claim_2', 'min_score'],
               'asmt_claim_2_score_max': ['claims', 'claim_2', 'max_score'],
               'asmt_claim_2_score_weight': ['claims', 'claim_2', 'weight'],
               'asmt_claim_3_score_min': ['claims', 'claim_3', 'min_score'],
               'asmt_claim_3_score_max': ['claims', 'claim_3', 'max_score'],
               'asmt_claim_3_score_weight': ['claims', 'claim_3', 'weight'],
               'asmt_claim_4_score_min': ['claims', 'claim_4', 'min_score'],
               'asmt_claim_4_score_max': ['claims', 'claim_4', 'max_score'],
               'asmt_claim_4_score_weight': ['claims', 'claim_4', 'weight'],
               'asmt_cut_point_1': ['performance_levels', 'level_2', 'cut_point'],
               'asmt_cut_point_2': ['performance_levels', 'level_3', 'cut_point'],
               'asmt_cut_point_3': ['performance_levels', 'level_4', 'cut_point'],
               'asmt_cut_point_4': ['performance_levels', 'level_5', 'cut_point']
           }

    # conf from file_loader
    conf = {
            'json_file': args.source_json,
            'mappings': mapping,
            'csv_table': 'csv_table_for_file_loader',
            'db_host': 'localhost',
            'db_port': '5432',
            'db_user': 'udl2',
            'db_name': 'udl2',
            'db_password': 'udl2abc1234',
            'csv_schema': 'udl2',
            'fdw_server': 'udl_import',
            'integration_schema': 'udl2',
            'integration_table': 'INT_SBAC_ASMT',
            'start_seq': 10,
            'batch_id': 100
    }
    load_json(conf)
