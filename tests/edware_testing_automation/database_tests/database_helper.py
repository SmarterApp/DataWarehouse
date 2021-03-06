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

"""
Created on Feb 13, 2013

@author: nparoha
"""
from sqlalchemy.sql import select

from edware_testing_automation.utils.db_connector import DBConnection
from edware_testing_automation.utils.db_utils import create_connection
from edware_testing_automation.utils.preferences import preferences, Edware
from edware_testing_automation.utils.test_base import EdTestBase


class DatabaseTestHelper(EdTestBase):
    db_url = None
    db_schema_name = None
    datasource_name = 'edware'

    def __init__(self, *args, **kwargs):
        EdTestBase.__init__(self, *args, **kwargs)
        DatabaseTestHelper.db_url = preferences(Edware.db_main_url)
        DatabaseTestHelper.db_schema_name = preferences(Edware.db_schema_name)
        create_connection(DatabaseTestHelper.db_url, DatabaseTestHelper.db_schema_name,
                          datasource_name=DatabaseTestHelper.datasource_name)

    # Find a specific table in the 'schema_name' schema
    def check_table_in_schema(self, table_name):
        found = False
        results = self.get_tables()
        for result in results:
            if table_name in result:
                found = True
                break
        self.assertTrue(found, 'Table {0} not found'.format(table_name))

    # Find the total number of tables in the 'schema_name' schema
    def get_number_of_tables(self, expected_num_tables):
        results = self.get_tables()
        actual_num_tables = len(results)
        self.assertEqual(actual_num_tables, expected_num_tables,
                         'Actual tables: {0} Expected # of tables: {1}'.format(actual_num_tables, expected_num_tables))

    # Validate that the table is not empty
    def check_table_not_empty(self, table_name):
        results = self.select_from_table(table_name)
        self.assertIsNotNone(len(results), 'Error: Table {0} is empty'.format(table_name))

    # query: select table_name from information_schema.tables where table_schema = schema_name;
    def get_tables(self):
        with DBConnection(name=DatabaseTestHelper.datasource_name) as connector:
            metadata = connector.get_metadata()
        return metadata.tables

    # query: select * from schema_name.table_name;
    def select_from_table(self, table):
        with DBConnection(name=DatabaseTestHelper.datasource_name) as connector:
            dim_table = connector.get_table(table)
            query = select([dim_table])
            results = connector.get_result(query)
        return results
