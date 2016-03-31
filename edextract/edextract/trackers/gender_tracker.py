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

__author__ = 'ablum'

"""
This module contains the definition of the MaleTracker and FemaleTracker classes,
which tracks visitor totals.
"""

from edextract.trackers.category_tracker import CategoryTracker
from edextract.student_reg_extract_processors.category_constants import CategoryNameConstants, CategoryValueConstants
from edextract.student_reg_extract_processors.attribute_constants import AttributeFieldConstants, AttributeValueConstants


class MaleTracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.SEX, CategoryValueConstants.MALE, AttributeFieldConstants.SEX)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.SEX] == AttributeValueConstants.MALE


class FemaleTracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.SEX, CategoryValueConstants.FEMALE, AttributeFieldConstants.SEX)

    def _should_increment(self, row):
        return row[AttributeFieldConstants.SEX] == AttributeValueConstants.FEMALE
