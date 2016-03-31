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
Created on Feb 8, 2013

@author: tosako
'''
import unittest
from sqlalchemy import String, Column
from edschema.database.connector import DBConnection
from edschema.metadata.ed_metadata import MetaColumn
from edschema.database.tests.utils.unittest_with_sqlite import Unittest_with_sqlite
import types


class TestEdMetadata(Unittest_with_sqlite):

    # Test dim_district data
    def test_dim_inst_hier_type(self):
        self.assertTrue('dim_inst_hier' in self.get_Metadata().tables, "missing dim_inst_hier")
        with DBConnection() as connector:
            dim_inst_hier = connector.get_table("dim_inst_hier")

            # check number of field in the table
            self.assertEqual(10, len(dim_inst_hier.c), "Number of fields in dim_district")

            query = dim_inst_hier.select(dim_inst_hier.c.district_id == '228')
            result = connector.get_result(query)
            self.assertEqual('228', result[0]['district_id'])

    # Test get_stream_result with dim_district_data
    def test_get_streaming_result(self):
        self.assertTrue('dim_inst_hier' in self.get_Metadata().tables, "missing dim_inst_hier")
        with DBConnection() as connector:
            dim_inst_hier = connector.get_table("dim_inst_hier")

            # check number of field in the table
            self.assertEqual(10, len(dim_inst_hier.c), "Number of fields in dim_district")

            query = dim_inst_hier.select(dim_inst_hier.c.district_id == '228')
            results = connector.get_streaming_result(query, fetch_size=1)
            self.assertEqual(type(results), types.GeneratorType)
            for result in results:
                self.assertEqual('228', result['district_id'])
                break
            # test for larger file out of fetch_size
            fact_asmt_outcome_vw = connector.get_table('fact_asmt_outcome_vw')
            query = fact_asmt_outcome_vw.select()
            results = connector.get_streaming_result(query, fetch_size=1)
            self.assertEqual(type(results), types.GeneratorType)
            counter = 0
            for result in results:
                counter = counter + 1
            self.assertEqual(counter, 1228)

    # Test student_registration data
    def test_student_registration(self):
        self.assertTrue('student_reg' in self.get_Metadata().tables, "missing student_reg")
        with DBConnection() as connector:
            fact_student_reg = connector.get_table("student_reg")

            # Check number of fields in the table
            self.assertEqual(40, len(fact_student_reg.c), "Number of fields in student_registration")

    def test_meta_column_col_type_attr(self):
        meta_column = MetaColumn('test_meta_column', String(50))
        self.assertEqual(getattr(meta_column, "col_type", "Column"), "MetaColumn")
        column = Column('test_column', String(50))
        self.assertEqual(getattr(column, "col_type", "Column"), "Column")

    def test_fact_block_outcome(self):
        self.assertTrue('fact_block_asmt_outcome' in self.get_Metadata().tables, "missing fact_block_asmt_outcome")
        with DBConnection() as connector:
            fact_student_reg = connector.get_table("fact_block_asmt_outcome")
            # Check number of fields in the table
            self.assertEqual(59, len(fact_student_reg.c), "Number of fields in fact_block_asmt_outcome")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
