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

'''
Utilities for cleaning up database tables
'''


def get_filtered_tables(connector, table_name_prefix=None):
    """This function returns list of tables starting with table_name_prefix from schema metadata

    :param connector: The connection to the database
    :returns : A list of table names
             [dim_student]
    """
    all_tables = []
    for table in connector.get_metadata().tables:
        # when schema is not specified, database name gets prepended
        if '.' in table:
            table = table.split('.')[1]
        if table_name_prefix is None or table.lower().startswith(table_name_prefix.lower()):
            all_tables.append(table)
    return all_tables


def cleanup_all_tables(connector, column_name, value, batch_delete=True, table_name_prefix=None, tables=None):
    """
    cleanup all tables for the given column and matching value

    All rows matching the given guid_batch will be delted from all the tables
    in the given connector schema
    """
    tables_to_cleanup = get_filtered_tables(connector, table_name_prefix) if tables is None else tables
    for table_name in tables_to_cleanup:
        table = connector.get_table(table_name)
        if column_name in table.columns:
            delete_query = table.delete(table.c[column_name] == value)
            connector.execute(delete_query)
