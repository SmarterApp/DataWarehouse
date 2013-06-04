'''
Created on Mar 8, 2013

@author: tosako
'''
import unittest
from smarter.tests.utils.unittest_with_smarter_sqlite import Unittest_with_smarter_sqlite_no_data_load,\
    UnittestSmarterDBConnection
from smarter.reports.compare_pop_report import QueryHelper
from smarter.reports.helpers.constants import Constants
from smarter.reports.exceptions.parameter_exception import InvalidParameterException


class Test(Unittest_with_smarter_sqlite_no_data_load):

    def test_build_columns_state_view(self):
        with UnittestSmarterDBConnection() as connection:
            helper = QueryHelper(connection, **get_param_state_view())
            columns = helper.build_columns()
            dim_inst_hier = connection.get_table(Constants.DIM_INST_HIER)
            dim_asmt = connection.get_table(Constants.DIM_ASMT)

        self.assertEquals(11, len(columns))
        # first three columns are for state view columns
        # test alias name
        self.assertEqual(columns[0].name, Constants.NAME, 'test for alias name')
        self.assertEqual(columns[0].element.table.name, dim_inst_hier.name)
        self.assertEqual(columns[0].element.name, dim_inst_hier.c.district_name.name)
        self.assertEqual(columns[1].name, Constants.ID, 'test for alias name')
        self.assertEqual(columns[1].element.table.name, dim_inst_hier.name)
        self.assertEqual(columns[1].element.name, dim_inst_hier.c.district_guid.name)
        self.assertEqual(columns[2].name, Constants.ASMT_SUBJECT, 'test for alias name')
        self.assertEqual(columns[2].element.table.name, dim_asmt.name)
        self.assertEqual(columns[2].element.name, dim_asmt.c.asmt_subject.name)
        self.check_asmt_custom_metadata(connection, columns[3])
        self.check_performance_level_columns(columns, 4)

    def test_build_columns_district_view(self):
        with UnittestSmarterDBConnection() as connection:
            helper = QueryHelper(connection, **get_param_district_view())
            columns = helper.build_columns()
            dim_inst_hier = connection.get_table(Constants.DIM_INST_HIER)
            dim_asmt = connection.get_table(Constants.DIM_ASMT)

        self.assertEquals(11, len(columns))
        # first three columns are for district view columns
        # test alias name
        self.assertEqual(columns[0].name, Constants.NAME, 'test for alias name')
        self.assertEqual(columns[0].element.table.name, dim_inst_hier.name)
        self.assertEqual(columns[0].element.name, dim_inst_hier.c.school_name.name)
        self.assertEqual(columns[1].name, Constants.ID, 'test for alias name')
        self.assertEqual(columns[1].element.table.name, dim_inst_hier.name)
        self.assertEqual(columns[1].element.name, dim_inst_hier.c.school_guid.name)
        self.assertEqual(columns[2].name, Constants.ASMT_SUBJECT, 'test for alias name')
        self.assertEqual(columns[2].element.table.name, dim_asmt.name)
        self.assertEqual(columns[2].element.name, dim_asmt.c.asmt_subject.name)
        self.check_asmt_custom_metadata(connection, columns[3])
        self.check_performance_level_columns(columns, 4)

    def test_build_columns_school_view(self):
        with UnittestSmarterDBConnection() as connection:
            helper = QueryHelper(connection, **get_param_school_view())
            columns = helper.build_columns()
            dim_asmt = connection.get_table(Constants.DIM_ASMT)
            fact_asmt_outcome = connection.get_table(Constants.FACT_ASMT_OUTCOME)

        self.assertEquals(11, len(columns))
        # first two columns are for school view columns
        # test alias name
        self.assertEqual(columns[0].name, Constants.NAME, 'test for alias name')
        self.assertEqual(columns[1].name, Constants.ID, 'test for alias name')
        self.assertEqual(columns[1].element.table.name, fact_asmt_outcome.name)
        self.assertEqual(columns[1].element.name, fact_asmt_outcome.c.asmt_grade.name)
        self.assertEqual(columns[2].name, Constants.ASMT_SUBJECT, 'test for alias name')
        self.assertEqual(columns[2].element.table.name, dim_asmt.name)
        self.assertEqual(columns[2].element.name, dim_asmt.c.asmt_subject.name)
        self.check_asmt_custom_metadata(connection, columns[3])
        self.check_performance_level_columns(columns, 4)

    def check_asmt_custom_metadata(self, connection, asmt_custom_metadata_column):
        dim_asmt = connection.get_table(Constants.DIM_ASMT)
        self.assertEqual(asmt_custom_metadata_column.name, Constants.ASMT_CUSTOM_METADATA)
        self.assertEqual(asmt_custom_metadata_column.element.table.name, dim_asmt.name)
        self.assertEqual(asmt_custom_metadata_column.element.name, dim_asmt.c.asmt_custom_metadata.name)

    def check_performance_level_columns(self, columns, offset):
        self.check_performance_level_column(columns[offset + 0], Constants.LEVEL1)
        self.check_performance_level_column(columns[offset + 1], Constants.LEVEL2)
        self.check_performance_level_column(columns[offset + 2], Constants.LEVEL3)
        self.check_performance_level_column(columns[offset + 3], Constants.LEVEL4)
        self.check_performance_level_column(columns[offset + 4], Constants.LEVEL5)

    def check_performance_level_column(self, column, alias_name):
        self.assertEqual(column.key, alias_name)

    def test_invalid_parameters(self):
        param = {'stateCode': 'DE', 'schoolGuid': 'BAC'}
        self.assertRaises(InvalidParameterException, QueryHelper, None, **param)


def get_param_school_view():
    return {Constants.STATECODE: 'AB', Constants.DISTRICTGUID: 'CD', Constants.SCHOOLGUID: 'EF'}


def get_param_district_view():
    return {Constants.STATECODE: 'AB', Constants.DISTRICTGUID: 'CD'}


def get_param_state_view():
    return {Constants.STATECODE: 'AB'}


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
