'''
Created on Jun 6, 2013

@author: swimberly
'''
import datetime

from sqlalchemy.sql.expression import select, bindparam
from sqlalchemy.exc import ProgrammingError
from edudl2.udl2_util.database_util import get_sqlalch_table_object,\
    create_sqlalch_session
from edudl2.rule_maker.rules.transformation_code_generator import generate_transformations


def populate_ref_column_map(conf_dict, db_engine, conn, schema_name, ref_table_name):
    '''
    Load the column mapping data to the specified reference table
    @param conf_dict: dict containing keys 'column_mappings'(the data) & 'column_definitions'(the column info)
                      the column definition information should not contain columns that are populated by db
    @param db_engine: sqlalchemy engine object
    @param conn: sqlalchemy connection object
    @param schema_name: the name of the reference schema
    @param ref_table_name: the name of the reference table for column mapping data
    '''
    col_map_table = get_sqlalch_table_object(db_engine, schema_name, ref_table_name)
    col_map_data = conf_dict['column_mappings']
    col_map_columns = conf_dict['column_definitions']
    data_list = []

    for row in col_map_data:
        row_map = {}
        for i in range(len(row)):
            row_map[col_map_columns[i]] = row[i]
        data_list.append(row_map)
    conn.execute(col_map_table.insert(), data_list)


def populate_stored_proc(engine, conn, ref_schema, ref_table_name):
    '''
    Generate and load stored procedures into the database
    @param engine: sqlalchemy engine object
    @param conn: sqlalchemy connection object
    @param ref_schema: the name of the reference schema
    @param ref_table_name: the name of the reference table containing the column mapping info
    @return: A list of tuples: (rule_name, proc_name)
    @rtype: list
    '''

    # get list of transformation rules
    trans_rules = get_transformation_rule_names(engine, conn, ref_schema, ref_table_name)

    # get list of stored procedures and code to generate
    proc_list = generate_transformations(trans_rules)
    rule_map_list = []

    # Create session to load all stored procedures
    session = create_sqlalch_session(engine)

    # add each procedure to db
    for proc in proc_list:
        if proc:
            rule_name = proc[0]
            proc_name = proc[1]
            proc_sql = proc[2]
            print('Creating function:', proc_name)

            # execute sql and all mappping to list
            try:
                session.execute(proc_sql)
                rule_map_list.append((rule_name, proc_name))
            except ProgrammingError as e:
                print('UNABLE TO CREATE FUNCTION: %s, Error: "%s"' % (proc_name, e))

    # commit session
    session.commit()

    # update db with stored proc names
    update_column_mappings(rule_map_list, engine, conn, ref_schema, ref_table_name)

    return rule_map_list


def get_transformation_rule_names(engine, conn, ref_schema, ref_table_name):
    '''
    Get a list of all used transformation rule names from the database
    @param engine: sqlalchemy engine object
    @param conn: sqlalchemy connection object
    @param ref_schema: the name of the reference schema
    @param ref_table_name: the name of the reference table containing the column mapping info
    @return: The list of transformations rules without duplicates
    @rtype: list
    '''

    # get column_mapping table object
    col_map_table = get_sqlalch_table_object(engine, ref_schema, ref_table_name)
    trans_rules = []

    # Create select statement to get distinct transformation rules
    select_stmt = select([col_map_table.c.transformation_rule]).distinct()

    # Put each rule in list and return
    for row in conn.execute(select_stmt):
        rule = row[0]
        if rule:
            trans_rules.append(rule)

    return trans_rules


def update_column_mappings(rule_map_list, engine, conn, ref_schema, ref_table_name):
    '''
    loop through the column mapping rows in the database and populate the
    stored procedure column based on the transformation name
    @param rule_map_list: A list of tuples containing mapping info. Tuples should be: (rule_name, proc_name)
    @param engine: sqlalchemy engine object
    @param conn: sqlalchemy connection object
    @param ref_schema: the name of the reference schema
    @param ref_table_name: the name of the reference table containing the column mapping info
    '''

    # check that list is not empty before preceding.
    if not rule_map_list:
        print('NO FUNCTIONS ADDED TO DATABASE')
        return

    # get column_mapping table object
    col_map_table = get_sqlalch_table_object(engine, ref_schema, ref_table_name)

    # Generate sql to perform update
    update_stmt = col_map_table.update().where(col_map_table.c.transformation_rule == bindparam('rule_name'))
    update_stmt = update_stmt.values(stored_proc_name=bindparam('proc_name'), stored_proc_created_date=datetime.datetime.now())

    value_list = []

    # Create list of dicts that sqlalchemy will recognize
    # to update all rules with corresponding stored procedure.
    for pair in rule_map_list:
        val_map = {'rule_name': pair[0], 'proc_name': pair[1]}
        value_list.append(val_map)

    # execute update statement
    conn.execute(update_stmt, value_list)
