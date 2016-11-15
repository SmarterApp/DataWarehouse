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

import unittest
from edextract.trackers.gender_tracker import MaleTracker, FemaleTracker

__author__ = 'ablum'


class TestGenderTracker(unittest.TestCase):

    def setUp(self):
        self.male_tracker = MaleTracker()
        self.female_tracker = FemaleTracker()
        self.valid_db_rows = [
            {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'sex': 'male'},
            {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2014, 'sex': 'male'},
            {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school2', 'academic_year': 2013, 'sex': 'male'},
            {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school2', 'academic_year': 2014, 'sex': 'male'},
            {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2013, 'sex': 'female'},
            {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school1', 'academic_year': 2014, 'sex': 'female'},
            {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school2', 'academic_year': 2013, 'sex': 'female'},
            {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'school2', 'academic_year': 2014, 'sex': 'female'},

        ]

        self.invalid_db_rows = [
            {'state_code': 'NJ', 'district_id': 'male_only_dis', 'school_id': 'male_only_school', 'academic_year': 2014, 'sex': 'male'},
            {'state_code': 'NJ', 'district_id': 'female_only_dis', 'school_id': 'female_only_school', 'academic_year': 2014, 'sex': 'female'},
            {'state_code': 'NJ', 'district_id': 'district1', 'school_id': 'BAD_VALUE_SCHOOL', 'academic_year': 2014, 'sex': 'BAD_VALUE'},
        ]

    def track_rows(self, track_function, rows):
        for row in rows:
            state_guid = row['state_code']
            district_id = row['district_id']
            school_id = row['school_id']
            track_function(state_guid, row)
            track_function(district_id, row)
            track_function(school_id, row)

    def validate_state_rows(self, tracker):
        self.assertEqual(2, len(tracker.get_map_entry('NJ')))
        self.assertEqual(2, tracker.get_map_entry('NJ')[2013])
        self.assertEqual(2, tracker.get_map_entry('NJ')[2014])

    def validate_district_rows(self, tracker):
        self.assertEqual(2, len(tracker.get_map_entry('district1')))
        self.assertEqual(2, tracker.get_map_entry('district1')[2013])
        self.assertEqual(2, tracker.get_map_entry('district1')[2014])

    def validate_school_rows(self, tracker):
        self.assertEqual(2, len(tracker.get_map_entry('school1')))
        self.assertEqual(1, tracker.get_map_entry('school1')[2013])
        self.assertEqual(1, tracker.get_map_entry('school1')[2014])

        self.assertEqual(2, len(tracker.get_map_entry('school2')))
        self.assertEqual(1, tracker.get_map_entry('school2')[2013])
        self.assertEqual(1, tracker.get_map_entry('school2')[2014])

    def validate_no_rows(self, tracker, guid):
        self.assertEqual(None, tracker.get_map_entry(guid))

    def test_male_tracker(self):
        self.track_rows(self.male_tracker.track_academic_year, self.valid_db_rows)

        self.validate_state_rows(self.male_tracker)
        self.validate_district_rows(self.male_tracker)
        self.validate_school_rows(self.male_tracker)

    def test_male_tracker_invalid_rows(self):
        self.track_rows(self.male_tracker.track_academic_year, self.invalid_db_rows)

        self.validate_no_rows(self.male_tracker, 'female_only_school')
        self.validate_no_rows(self.male_tracker, 'female_only_district')
        self.validate_no_rows(self.male_tracker, 'BAD_VALUE_SCHOOL')

    def test_female_tracker(self):
        self.track_rows(self.female_tracker.track_academic_year, self.valid_db_rows)

        self.validate_state_rows(self.female_tracker)
        self.validate_district_rows(self.female_tracker)
        self.validate_school_rows(self.female_tracker)

    def test_female_tracker_invalid_rows(self):
        self.track_rows(self.female_tracker.track_academic_year, self.invalid_db_rows)

        self.validate_no_rows(self.female_tracker, 'male_only_school')
        self.validate_no_rows(self.female_tracker, 'male_only_district')
        self.validate_no_rows(self.female_tracker, 'BAD_VALUE_SCHOOL')
