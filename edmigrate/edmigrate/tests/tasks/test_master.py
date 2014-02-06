__author__ = 'sravi'

import unittest
import edmigrate.tasks.master as master
from edcore.tests.utils.unittest_with_repmgr_sqlite import Unittest_with_repmgr_sqlite, \
    Unittest_with_repmgr_sqlite_no_data_load, UnittestRepMgrDBConnection


class TestMasterWorker(Unittest_with_repmgr_sqlite):

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        Unittest_with_repmgr_sqlite.setUpClass()

    def tearDown(self):
        pass

    def test_verify_master_slave_repl_status(self):
        self.assertTrue(master.verify_slaves_repl_status('repmgr', ['dbpgdwr0.qa.dum.edwdc.net', 'dbpgdwr0s1.qa.dum.edwdc.net'], 10))
        self.assertFalse(master.verify_slaves_repl_status('repmgr', ['dbpgdwr0.qa.dum.edwdc.net', 'dbpgdwr0s1.qa.dum.edwdc.net'], -1))

if __name__ == "__main__":
    unittest.main()
