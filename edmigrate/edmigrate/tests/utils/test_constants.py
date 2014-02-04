'''
Created on Feb 4, 2014

@author: ejen
'''
__author__ = 'ejen'

import unittest
from edmigrate.utils.constants import Constants
from edcore.tests.utils.unittest_with_repmgr_sqlite import Unittest_with_repmgr_sqlite, \
    Unittest_with_repmgr_sqlite_no_data_load, UnittestRepMgrDBConnection


class TestConstants(Unittest_with_repmgr_sqlite):

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        Unittest_with_repmgr_sqlite.setUpClass()

    def tearDown(self):
        pass

    def test_constants(self):
        self.assertEqual(Constants.REPL_MGR_SCHEMA, 'repmgr_edware_pg_cluster')
        self.assertEqual(Constants.REPL_STATUS_TABLE, 'repl_status')
        self.assertEqual(Constants.REPL_NODES_TABLE, 'repl_nodes')
        self.assertEqual(Constants.REPL_NODE_CONN_INFO, 'conninfo')
        self.assertEqual(Constants.REPL_STANDBY_NODE, 'standby_node')
        self.assertEqual(Constants.REPL_STATUS_LAG, 'replication_lag')
        self.assertEqual(Constants.REPL_NODE_ID, 'id')
        self.assertEqual(Constants.SLAVE_GROUP_A, 'A')
        self.assertEqual(Constants.SLAVE_GROUP_B, 'B')


if __name__ == "__main__":
    unittest.main()
