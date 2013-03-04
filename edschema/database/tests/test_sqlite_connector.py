'''
Created on Feb 28, 2013

@author: tosako
'''
import unittest
from database.sqlite_connector import create_sqlite
from zope import component
from database.connector import IDbUtil


class Test(unittest.TestCase):

    def test_create_engine(self):
        # Make sure we do not have sqlite in memory
        dbUtil = component.queryUtility(IDbUtil)
        self.assertIsNone(dbUtil)

        create_sqlite(force_foreign_keys=True, use_metadata_from_db=False, echo=False)
        dbUtil = component.queryUtility(IDbUtil)
        engine = dbUtil.get_engine()
        metadata = dbUtil.get_metadata()
        self.assertIsNotNone(engine)
        self.assertIsNotNone(metadata)

    def test_list_of_tables_from_db(self):
        create_sqlite(force_foreign_keys=True, use_metadata_from_db=True, echo=False)
        dbUtil = component.queryUtility(IDbUtil)
        engine = dbUtil.get_engine()
        metadata = dbUtil.get_metadata()
        self.assertIsNotNone(engine)
        self.assertIsNotNone(metadata)
        self.assertIsNotNone(metadata.tables.keys())

    def test_list_of_tables_by_using_foreign_keys_deps(self):
        create_sqlite(force_foreign_keys=True, use_metadata_from_db=True, echo=False)
        dbUtil = component.queryUtility(IDbUtil)
        metadata = dbUtil.get_metadata()
        sorted_tables = metadata.sorted_tables
        self.assertIsNotNone(sorted_tables)

        # fact_asmt_outcome has Foreign keys from dim_asmt, dim_inst_hier, and dim_section_subject
        self.assertTrue(check_order_of_fact_asmt_outcome(sorted_tables))


def check_order_of_fact_asmt_outcome(sorted_tables):
    foreign_keys_tables = ['dim_asmt', 'dim_inst_hier', 'dim_section_subject']
    for table in sorted_tables:
        if table.key == 'fact_asmt_outcome':
            # check foreign_keys_tables.
            if len(foreign_keys_tables) == 0:
                return True
            else:
                return False
        if table.key in foreign_keys_tables:
            foreign_keys_tables.remove(table.key)
    return False

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
