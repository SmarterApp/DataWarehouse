import compare_populations_districts_within_state
import compare_populations_schools_within_district
import unittest

class ComparePopulations(unittest.TestCase):

    def test_compare_populations_districts_within_state(self):

        expected_scorelist = compare_populations_districts_within_state.districts_in_a_state('DE', 'SUMMATIVE', 'ELA')
        
    def test_compare_populations_schools_within_district(self):

        expected_scorelist = compare_populations_schools_within_district.schools_in_a_district(161, 'SUMMATIVE', 'ELA')
        

   