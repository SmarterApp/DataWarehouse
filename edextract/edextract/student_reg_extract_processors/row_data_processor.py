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

__author__ = 'tshewchuk'

from edextract.student_reg_extract_processors.district_data_processor import DistrictDataProcessor
from edextract.student_reg_extract_processors.school_data_processor import SchoolDataProcessor
from edextract.student_reg_extract_processors.state_data_processor import StateDataProcessor
from edextract.trackers.total_tracker import TotalTracker
from edextract.trackers.gender_tracker import FemaleTracker, MaleTracker
from edextract.trackers.race_tracker import (HispanicLatinoTracker, AmericanIndianTracker, AsianTracker, AfricanAmericanTracker,
                                             PacificIslanderTracker, WhiteTracker, MultiRaceTracker)
from edextract.trackers.program_tracker import (IDEAIndicatorTracker, LEPStatusTracker, Sec504StatusTracker,
                                                EconDisadvStatusTracker, MigrantStatusTracker)
from edextract.trackers.grade_tracker import (GradeKTracker, Grade1Tracker, Grade2Tracker, Grade3Tracker, Grade4Tracker,
                                              Grade5Tracker, Grade6Tracker, Grade7Tracker, Grade8Tracker, Grade9Tracker,
                                              Grade10Tracker, Grade11Tracker, Grade12Tracker)

"""
This module contain functions to process iterator row data using data processors and trackers.
"""


class RowDataProcessor():

    def __init__(self):
        self.total_tracker = TotalTracker()
        self.trackers = [self.total_tracker, MaleTracker(), FemaleTracker(), HispanicLatinoTracker(), AmericanIndianTracker(),
                         AsianTracker(), AfricanAmericanTracker(), PacificIslanderTracker(), WhiteTracker(), MultiRaceTracker(),
                         IDEAIndicatorTracker(), LEPStatusTracker(), Sec504StatusTracker(), EconDisadvStatusTracker(),
                         MigrantStatusTracker(), GradeKTracker(), Grade1Tracker(), Grade2Tracker(), Grade3Tracker(),
                         Grade4Tracker(), Grade5Tracker(), Grade6Tracker(), Grade7Tracker(), Grade8Tracker(), Grade9Tracker(),
                         Grade10Tracker(), Grade11Tracker(), Grade12Tracker()]
        self.data_processors = [StateDataProcessor(self.trackers), DistrictDataProcessor(self.trackers), SchoolDataProcessor(self.trackers)]

    def process_yearly_row_data(self, rows):
        """
        Iterate through the database results, processing each academic year row
        @param: rows: Iterable containing all pertinent database rows
        """

        functions = [p.process_yearly_data for p in self.data_processors]
        self._process(rows, functions)

    def process_matched_ids_row_data(self, rows):
        """
        Iterate through the database results, processing each matched ids row
        @param: rows: Iterable containing all pertinent database rows
        """

        functions = [p.process_matched_ids_data for p in self.data_processors]
        self._process(rows, functions)

    def process_asmt_outcome_row_data(self, rows):
        """
        Iterate through the database results, processing each assessment and student reg data row
        @param: rows: Iterable containing all pertinent database rows
        """

        functions = [p.process_asmt_outcome_data for p in self.data_processors]
        self._process(rows, functions)

    def _process(self, rows, functions):
        for row in rows:
            for process_func in functions:
                process_func(row)
