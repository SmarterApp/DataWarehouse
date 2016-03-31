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

from edextract.student_reg_extract_processors.district_data_processor import DistrictDataProcessor

__author__ = 'ablum'

"""
Test Student Registration District Data Processor
"""

import unittest
from edextract.student_reg_extract_processors.attribute_constants import AttributeFieldConstants
from unittest.mock import MagicMock


class TestDistrictDataProcessor(unittest.TestCase):

    def setUp(self):
        self.results = {AttributeFieldConstants.STATE_NAME: 'North Carolina', AttributeFieldConstants.STATE_CODE: 'NC',
                        AttributeFieldConstants.DISTRICT_ID: 'GUILFORD_GUID', AttributeFieldConstants.DISTRICT_NAME: 'Guilford County'}

        self.matched_ids_results = {AttributeFieldConstants.STATE_NAME: 'North Carolina', AttributeFieldConstants.STATE_CODE: 'NC',
                                    AttributeFieldConstants.DISTRICT_ID: 'GUILFORD_GUID', AttributeFieldConstants.DISTRICT_NAME: 'Guilford County',
                                    'prev_district_id': 'GUILFORD_GUID'}

        self.category_trackers = []

        self.district_data_processor = DistrictDataProcessor(self.category_trackers)

    def test_ed_org_map_updates(self):
        self.district_data_processor.process_yearly_data(self.results)
        self.assertEquals(len(self.district_data_processor.get_ed_org_hierarchy()), 1)
        self.assertDictEqual(self.district_data_processor.get_ed_org_hierarchy(), {('North Carolina', 'Guilford County', ''): 'GUILFORD_GUID'})

    def test_call_to_tracker(self):
        self.district_data_processor._call_academic_year_trackers = MagicMock(return_value=None)

        self.district_data_processor.process_yearly_data(self.results)

        self.district_data_processor._call_academic_year_trackers.assert_called_with('GUILFORD_GUID', self.results)

    def test_call_to_matched_ids_tracker(self):
        self.district_data_processor._call_matched_ids_trackers = MagicMock(return_value=None)

        self.district_data_processor.process_matched_ids_data(self.matched_ids_results)

        self.district_data_processor._call_matched_ids_trackers.assert_called_with('GUILFORD_GUID', self.matched_ids_results)

    def test__should_call_trackers(self):
        same_districts = {AttributeFieldConstants.DISTRICT_ID: 'GUILFORD_GUID', 'prev_district_id': 'GUILFORD_GUID'}
        result = self.district_data_processor._is_matched_district(same_districts)
        self.assertTrue(result)

    def test__should_not_call_trackers(self):
        different_districts = {AttributeFieldConstants.DISTRICT_ID: 'GUILFORD_GUID', 'prev_district_id': 'NOTGUILFORDGUID'}
        result = self.district_data_processor._is_matched_district(different_districts)
        self.assertFalse(result)

    def test_process_asmt_outcome_data(self):
        self.district_data_processor._call_asmt_trackers = MagicMock(return_value=None)

        self.district_data_processor.process_asmt_outcome_data(self.results)

        self.district_data_processor._call_asmt_trackers.assert_called_with('GUILFORD_GUID', self.results)
