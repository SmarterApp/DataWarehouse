__author__ = 'npandey'

"""
Track the counts for ethnicity/race category
"""

from edextract.student_reg_extract_processors.attribute_constants import AttributeFieldConstants
from edextract.student_reg_extract_processors.category_constants import CategoryNameConstants, CategoryValueConstants
from edextract.trackers.category_tracker import CategoryTracker


class HispanicLatinoTracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.ETHNICITY, CategoryValueConstants.HISPANIC_ETH)

    def should_increment(self, row):
        return row[AttributeFieldConstants.HISPANIC_ETH]


class AmericanIndianTracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.RACE, CategoryValueConstants.AMERICAN_INDIAN)

    def should_increment(self, row):
        return row[AttributeFieldConstants.AMERICAN_INDIAN]


class AsianTracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.RACE, CategoryValueConstants.ASIAN)

    def should_increment(self, row):
        return row[AttributeFieldConstants.ASIAN]


class AfricanAmericanTracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.RACE, CategoryValueConstants.AFRICAN_AMERICAN)

    def should_increment(self, row):
        return row[AttributeFieldConstants.AFRICAN_AMERICAN]


class PacificIslanderTracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.RACE, CategoryValueConstants.PACIFIC)

    def should_increment(self, row):
        return row[AttributeFieldConstants.PACIFIC]


class WhiteTracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.RACE, CategoryValueConstants.WHITE)

    def should_increment(self, row):
        return row[AttributeFieldConstants.WHITE]


class MultiRaceTracker(CategoryTracker):

    def __init__(self):
        super().__init__(CategoryNameConstants.RACE, CategoryValueConstants.MULTI_RACE)

    def should_increment(self, row):
        return row[AttributeFieldConstants.MULTI_RACE]
