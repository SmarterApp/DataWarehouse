'''
Created on May 13, 2013

@author: swimberly
'''

from argparse import ArgumentParser
from importlib import import_module
import time
import os
import sys
import inspect
import subprocess

CMD_FOLDER = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
HENSHIN_FOLDER = CMD_FOLDER.replace(os.path.join('CreateGenerateLoad', 'src'), os.path.join('Henshin', 'src'))
DATA_LOAD_FOLDER = CMD_FOLDER.replace(os.path.join('CreateGenerateLoad', 'src'), os.path.join('DataGeneration', 'dataload'))
DATA_INFO_MODULE = 'datainfo.best_worst_results'
LOAD_DATA_MODULE = 'load_data'
HENSHIN_MODULE = 'henshin'


def main(schema, database, host, user, passwd, port=5432, create=True, landing_zone=True, best_worst=True, config_file=None):
    '''
    '''
    start_time = time.time()

    if create:
        print('Creating schema "%s" in database "%s" at "%s"' % (schema, database, host))
        create_schema(schema, database, host, user, passwd)

    print('Generating New Data')
    csv_dir = generate_data(config_file)

    print('Loading New Data')
    load_data(csv_dir, schema, database, host, user, passwd, port)

    if landing_zone:
        print('Transforming to landing zone')
        transform_to_landing_zone(csv_dir, schema, database, host, user, passwd, port)

    if best_worst:
        print('Getting Best and worst assessment performances')
        get_data_info(schema, database, host, user, passwd, port)

    tot_time = time.time() - start_time
    print('All steps completed in %.2fs' % tot_time)


def create_schema(schema_name, database, host, user, passwd):
    print('cloning edware repo to run the ed_schema code')
    folder = get_ed_schema_code()
    ed_schema_file = os.path.join(folder, 'edschema', 'edschema', 'ed_metadata.py')
    output = system('python', ed_schema_file, '-s', schema_name, '-d', database, '--host', host, '-u', user, '-p', passwd)
    print(output.decode('UTF-8'))


def generate_data(config_file=None):
    print('Generating Data')

    gen_data_loc = os.path.join(CMD_FOLDER, '..', '..', 'DataGeneration', 'src', 'generate_data.py')
    gen_data_output = os.path.join(CMD_FOLDER, '..', '..', 'DataGeneration', 'datafiles', 'csv')

    if config_file:
        output = system('python', gen_data_loc, '--config', config_file)
    else:
        output = system('python', gen_data_loc)

    print(output.decode('UTF-8'))
    print('Data Generation Complete')
    return gen_data_output


def load_data(csv_dir, schema, database, host, user, passwd, port):
    '''
    Load data into schema
    '''

    load_data_loc = os.path.join(CMD_FOLDER, '..', '..', 'DataGeneration', 'dataload', 'load_data.py')

    output = system('python', load_data_loc, '-c', csv_dir, '-d', database, '--host', host, '-u', user, '-t', schema, passwd)
    print(output.decode('UTF-8'))


def get_data_info(schema, database, host, user, passwd, port):
    '''
    run the data info script
    '''

    data_info_path = os.path.join(CMD_FOLDER, '..', '..', 'DataGeneration', 'dataload', 'datainfo', 'best_worst_results.py')

    output = system('python', data_info_path, '--password', passwd, '--schema', schema, '-s', host, '-d', database, '-u', user, '--csv', '--bestworst')
    print(output.decode('UTF-8'))


def transform_to_landing_zone(csv_dir, schema, database, host, user, passwd, port):
    '''
    Call the Henshin script. Return the path to the output.
    '''
    henshin_path = os.path.join(CMD_FOLDER, '..', '..', 'Henshin', 'src', 'henshin.py')
    output_path = os.path.join(CMD_FOLDER, 'henshin_out')
    dim_asmt_path = os.path.join(csv_dir, 'dim_asmt.csv')

    output = system('python', henshin_path, '-d', dim_asmt_path, '-o', output_path, '--password', passwd, '--schema', schema, '--host', host, '--database', database, '-u', user)
    print(output.decode('UTF-8'))
    return output_path


def get_input_args():
    '''
    Creates parser for command line args
    @return: args A namespace of the command line args
    '''

    parser = ArgumentParser(description='Script to get best or worst Students, Districts and Schools')
    parser.add_argument('-c', '--create', action='store_true', help='create a new schema')
    parser.add_argument('-l', '--landing-zone', action='store_true', help='flag generate landing zone file format')
    parser.add_argument('-b', '--best-worst', action='store_true', help='flag to create csv files that show the best and worst performers in the data')
    parser.add_argument('-s', '--schema', required=True, help='the name of the schema to use')
    parser.add_argument('-d', '--database', default='edware', help='the name of the database to connect to. Default: "edware"')
    parser.add_argument('-u', '--username', default='edware', help='the username for the database')
    parser.add_argument('-p', '--passwd', default='edware', help='the password to use for the database')
    parser.add_argument('--host', default='localhost', help='the host to connect to. Default: "localhost"')
    parser.add_argument('--port', default=5432, help='the port number')
    parser.add_argument('--data-gen-config-file', help='a configuration file to use for data generation')

    return parser.parse_args()


def get_ed_schema_code(tmp_folder='ed_schema_temp'):
    '''
    Clone edware repository so that the schema creation can be done.
    @keyword tmp_folder: the name of the directory to store the edware repo
    @return: tmp_folder -- the name of the folder where the folder was clone
    '''
    repo_path = 'git@github.wgenhq.net:Ed-Ware-SBAC/edware.git'
    system('git', 'clone', repo_path, tmp_folder)
    return tmp_folder


def system(*args, **kwargs):
    '''
    Method for running system calls
    Taken from the pre-commit file for python3 in the scripts directory
    '''
    kwargs.setdefault('stdout', subprocess.PIPE)
    proc = subprocess.Popen(args, **kwargs)
    out, _err = proc.communicate()
    return out


if __name__ == '__main__':
    input_args = get_input_args()
    main(input_args.schema, input_args.database, input_args.host, input_args.username, input_args.passwd, input_args.port, input_args.create, input_args.landing_zone, input_args.best_worst, input_args.data_gen_config_file)
