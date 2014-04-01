__author__ = 'tshewchuk'

"""
This module contains the definition of the TotalTracker class, which tracks visitor totals.
"""

from edextract.trackers.category_tracker import CategoryTracker
from edextract.student_reg_extract_processors.category_constants import CategoryNameConstants, CategoryValueConstants


class TotalTracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.TOTAL, CategoryValueConstants.TOTAL)

    def should_increment_year(self, row):
        return True

    def should_increment_matched_ids(self, row):
        return
