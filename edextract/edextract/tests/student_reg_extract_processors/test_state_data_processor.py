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

__author__ = 'npandey'
"""
Test Student Registration State Data Processor
"""

from edextract.student_reg_extract_processors.state_data_processor import StateDataProcessor
import unittest
from edextract.student_reg_extract_processors.attribute_constants import AttributeFieldConstants
from unittest.mock import MagicMock


class TestStateDataProcessor(unittest.TestCase):

    def setUp(self):
        self.results = {AttributeFieldConstants.STATE_NAME: 'North Carolina', AttributeFieldConstants.STATE_CODE: 'NC'}
        self.category_trackers = []

        self.state_data_processor = StateDataProcessor(self.category_trackers)

    def test_ed_org_map_updates(self):
        self.state_data_processor.process_yearly_data(self.results)
        self.assertEqual(len(self.state_data_processor.get_ed_org_hierarchy()), 1)
        self.assertDictEqual(self.state_data_processor.get_ed_org_hierarchy(), {('North Carolina', '', ''): 'NC'})

    def test_call_to_tracker(self):
        self.state_data_processor._call_academic_year_trackers = MagicMock(return_value=None)

        self.state_data_processor.process_yearly_data(self.results)

        self.state_data_processor._call_academic_year_trackers.assert_called_with('NC', self.results)

    def test_call_to_matched_ids_tracker(self):
        self.state_data_processor._call_matched_ids_trackers = MagicMock(return_value=None)

        self.state_data_processor.process_matched_ids_data(self.results)

        self.state_data_processor._call_matched_ids_trackers.assert_called_with('NC', self.results)

    def test_process_asmt_outcome_data(self):
        self.state_data_processor._call_asmt_trackers = MagicMock(return_value=None)

        self.state_data_processor.process_asmt_outcome_data(self.results)

        self.state_data_processor._call_asmt_trackers.assert_called_with('NC', self.results)
