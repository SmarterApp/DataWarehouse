'''
Created on Feb 28, 2013

@author: tosako
'''
import argparse
from database.sqlite_connector import create_sqlite, destroy_sqlite
import os
from zope import component
from database.connector import IDbUtil
import sys
import csv
from database.data_importer import import_csv_dir


def read_csv(dir_name):
    '''
    Read csv file from the directory
    '''
    csv_file_map = {}
    csv_file_list = []
    if os.path.exists(dir_name):
        csv_file_list = [f for f in os.listdir(dir_name) if f.endswith('.csv')]
    for file in csv_file_list:
        base_csv_file_name = os.path.basename(file)[:-4]
        csv_file_map[base_csv_file_name] = os.path.join(dir_name, file)
    return csv_file_map


def get_list_of_tables(force_foreign_keys=True):
    '''
    Read tables from metadata
    '''
    tables = []
    metadata = component.queryUtility(IDbUtil).get_metadata()
    if force_foreign_keys:
        tables = metadata.sorted_tables
    else:
        tables = metadata.tables
    return list(tables)


def check_tables(list_tables, csv_file_map):
    '''
    Check list of tables against list of csv files.
    return missing list of tables and unnecessary csv files
    '''
    table_lookup = {}
    for table in list_tables:
        table_lookup[table.name] = table
    missing_file_for_tables = list(list_tables)
    unnecessary_files = list(csv_file_map.keys())
    for csv_name in csv_file_map.keys():
        if csv_name in table_lookup:
            missing_file_for_tables.remove(table_lookup[csv_name])
            unnecessary_files.remove(csv_name)

    return missing_file_for_tables, unnecessary_files


def read_fields_name(target_csv_file):
    '''
    return list of field name from csv
    '''
    field_names = []
    with open(target_csv_file) as file_obj:
        # first row of the csv file is the header names
        reader = csv.DictReader(file_obj, delimiter=',')
        field_names = reader.fieldnames
    return field_names


def check_fields(target_table, target_csv_file):
    '''
    check whether filds are missing from csv file or not.
    First line always list of fields; otherwise, return None immediately
    return tuplet, if everything is okay, each values in the tuplet is empty.
    '''
    missing_fields = []
    unnecessary_fields = []
    list_of_fields = read_fields_name(target_csv_file)
    unnecessary_fields = list(list_of_fields)
    for column in target_table.c:
        if column.name in list_of_fields:
            unnecessary_fields.remove(column.name)
        else:
            missing_fields.append(column.name)

    return missing_fields, unnecessary_fields


def run_validation(metadata=None, force_foreign=True, missing_table_ignore=False, missing_field_ignore=False, dir_name='/please_specify_dir', verbose=False):
    create_sqlite(force_foreign_keys=force_foreign, use_metadata_from_db=False, echo=verbose, metadata=metadata)
    if not os.path.exists(dir_name):
        return 1
    csv_file_map = read_csv(dir_name)
    tables = get_list_of_tables(force_foreign)

    # check table consistency
    if not missing_table_ignore:
        missing_file_for_tables, unnecessary_files = check_tables(tables, csv_file_map)
        exit_me = False
        if len(missing_file_for_tables) > 0:
            print('No CSV file(s) for following table(s):')
            for table in missing_file_for_tables:
                print('    ' + table.name)
            exit_me = True
        if len(unnecessary_files) > 0:
            print('Unnecessary CSV file(s):')
            for file in unnecessary_files:
                print('    ' + file)
            exit_me = True
        if exit_me:
            return __exit_run_validation(1)

    # check field consistency
    if not missing_field_ignore:
        exit_me = False
        for table in tables:
            if table.name in csv_file_map:
                missing_fields, unnecessary_fields = check_fields(table, csv_file_map[table.name])
                if len(missing_fields) > 0:
                    print('cvs[%s]: missing field(s):' % csv_file_map[table.name])
                    for field in missing_fields:
                        print('    ' + field)
                    exit_me = True
                if len(unnecessary_fields) > 0:
                    print('cvs[%s]: unnecessary field(s):' % csv_file_map[table.name])
                    for field in unnecessary_fields:
                        print('    ' + field)
                    exit_me = True
        if exit_me:
            return __exit_run_validation(1)

    # import data
    import_ok = import_csv_dir(dir_name)
    if not import_ok:
        print('failed to import csv data')
    return __exit_run_validation(0)


def __exit_run_validation(exit_code):
    destroy_sqlite()
    return exit_code


def main():
    parser = argparse.ArgumentParser(description='Validating for EdWare Data')
    parser.add_argument("-d", "--dir", help="Specify a csv directory")
    parser.add_argument("-n", "--no-foreign", help="Disable Foreign key constraint", action='store_true', default=False)
    parser.add_argument("-t", "--table-ignore", help="Ignore missing tables", action='store_true', default=False)
    parser.add_argument("-f", "--field-ignore", help="Ignore missing fields", action='store_true', default=False)
    parser.add_argument("-v", "--verbose", help="Verbose", action='store_true', default=False)
    args = parser.parse_args()

    __dir_name = args.dir
    if __dir_name is None:
        print('please specify a directory.  use -d')
        sys.exit(1)
    __force_foreign = not args.no_foreign
    __missing_table_ignore = args.table_ignore
    __missing_field_ignore = args.field_ignore
    __verbose = args.verbose

    rtn_value = run_validation(force_foreign=__force_foreign, missing_table_ignore=__missing_table_ignore, missing_field_ignore=__missing_field_ignore, dir_name=__dir_name, verbose=__verbose)

    print('###################')
    if rtn_value != 0:
        print('Validation: FAIL')
    else:
        print('Validation: SUCCESS')
    sys.exit(rtn_value)

if __name__ == '__main__':
    main()
