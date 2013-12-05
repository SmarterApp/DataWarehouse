'''
Created on Nov 16, 2013

@author: dip
'''
import unittest
from smarter.extract.format import setup_input_file_format, get_column_mapping
from smarter.reports.helpers.constants import Constants


class TestFormat(unittest.TestCase):

    def setUp(self):
        setup_input_file_format()

    def test_dim_asmt_mapping_from_json(self):
        dim_asmt = get_column_mapping(Constants.DIM_ASMT, True)
        self.assertIsNotNone(dim_asmt)
        self.assertEqual(dim_asmt['asmt_guid'], 'identification.guid')
        self.assertEqual(dim_asmt['asmt_claim_1_name'], 'claims.claim_1.name')
        self.assertEqual(dim_asmt['asmt_perf_lvl_name_1'], 'performance_levels.level_1.name')
        self.assertEqual(dim_asmt['asmt_score_min'], 'overall.min_score')
        self.assertEqual(dim_asmt['asmt_claim_1_score_max'], 'claims.claim_1.max_score')
        self.assertEqual(dim_asmt['asmt_claim_2_score_weight'], 'claims.claim_2.weight')
        self.assertEqual(dim_asmt['asmt_cut_point_3'], 'performance_levels.level_4.cut_point')

    def test_workaround_with_asmt_guid(self):
        dim_asmt = get_column_mapping(Constants.DIM_ASMT)
        self.assertIsNotNone(dim_asmt)
        self.assertEqual(dim_asmt['asmt_guid'], 'guid_asmt')

    def test_dim_student_mapping(self):
        dim_student = get_column_mapping(Constants.DIM_STUDENT)
        self.assertIsNotNone(dim_student)
        self.assertEqual(dim_student['student_guid'], 'guid_student')
        self.assertEqual(dim_student['first_name'], 'name_student_first')
        self.assertEqual(dim_student['address_1'], 'address_student_line1')
        self.assertEqual(dim_student['gender'], 'gender_student')
        self.assertEqual(dim_student['email'], 'email_student')
        self.assertEqual(dim_student['dob'], 'dob_student')
        self.assertEqual(dim_student['grade'], 'grade_enrolled')
        self.assertEqual(dim_student['state_code'], 'code_state')
        self.assertEqual(dim_student['school_guid'], 'guid_school')

    def test_dim_inst_hier(self):
        dim_inst = get_column_mapping(Constants.DIM_INST_HIER)
        self.assertIsNotNone(dim_inst)
        self.assertEqual(dim_inst['state_name'], 'name_state')
        self.assertEqual(dim_inst['state_code'], 'code_state')
        self.assertEqual(dim_inst['district_guid'], 'guid_district')
        self.assertEqual(dim_inst['district_name'], 'name_district')
        self.assertEqual(dim_inst['school_category'], 'type_school')

    def test_fact_asmt_outcome(self):
        fact = get_column_mapping(Constants.FACT_ASMT_OUTCOME)
        self.assertIsNotNone(fact)
        self.assertEqual(fact['student_guid'], 'guid_student')
        self.assertEqual(fact['where_taken_id'], 'guid_asmt_location')
        self.assertEqual(fact['where_taken_name'], 'name_asmt_location')
        self.assertEqual(fact['enrl_grade'], 'grade_enrolled')
        self.assertEqual(fact['date_taken'], 'date_assessed')
        self.assertEqual(fact['date_taken_day'], 'date_assessed')
        self.assertEqual(fact['date_taken_month'], 'date_assessed')
        self.assertEqual(fact['date_taken_year'], 'date_assessed')
        self.assertEqual(fact['asmt_score'], 'score_asmt')
        self.assertEqual(fact['asmt_score_range_min'], 'score_asmt_min')
        self.assertEqual(fact['asmt_perf_lvl'], 'score_perf_level')
        self.assertEqual(fact['asmt_claim_1_score'], 'score_claim_1')
        self.assertEqual(fact['asmt_claim_1_score_range_max'], 'score_claim_1_max')
        self.assertEqual(fact['gender'], 'gender_student')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
