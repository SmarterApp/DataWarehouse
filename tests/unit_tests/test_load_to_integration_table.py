'''
Created on May 24, 2013

@author: ejen
'''
import sys
import os
import unittest
import logging
from udl2.database import UDL_METADATA
from udl2_util.database_util import connect_db, execute_queries, get_table_columns_info
from move_to_integration.move_to_integration import move_data_from_staging_to_integration, create_migration_query
from udl2.defaults import UDL2_DEFAULT_CONFIG_PATH_FILE
import imp
import re


class TestLoadToIntegrationTable(unittest.TestCase):

    def setUp(self, ):
        pass

    def tearDown(self, ):
        pass

    def test_move_data_from_staging_to_integration(self, ):
        pass

    def test_create_migration_query(self, ):
        pass
    

if __name__ == '__main__':
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
