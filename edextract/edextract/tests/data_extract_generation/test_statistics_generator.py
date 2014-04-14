import unittest

from collections import OrderedDict

from edextract.data_extract_generation.statistics_generator import get_tracker_results
from edextract.trackers.total_tracker import TotalTracker
from edextract.student_reg_extract_processors.ed_org_data_processor import EdOrgNameKey

__author__ = 'ablum'


class TestStatisticsGenerator(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_tracker_results(self):
        report_map = OrderedDict([
            (EdOrgNameKey('New Jersey', '', ''), 'NJ'),
            (EdOrgNameKey('New Jersey', 'Central Regional', ''), 'district1'),
            (EdOrgNameKey('New Jersey', 'Capital Regional', ''), 'district2'),
            (EdOrgNameKey('New Jersey', 'Central Regional', 'Springfield Elementary'), 'school1'),
            (EdOrgNameKey('New Jersey', 'Central Regional', 'Springfield Junior High'), 'school2'),
            (EdOrgNameKey('New Jersey', 'Capital Regional', 'Capital Charter School'), 'school3'),
            (EdOrgNameKey('New Jersey', 'Capital Regional', 'Capital School Of Interpretive Dance'), 'school4')
        ])
        total_tracker = TotalTracker()
        trackers = [total_tracker]
        total_tracker._data_counter.map = {
            'NJ': {2014: 444, 2015: 555, 'matched_ids': 333},
            'district1': {2014: 123, 2015: 90, 'matched_ids': 100},
            'district2': {2014: 20, 2015: 20, 'matched_ids': 18},
            'school1': {2014: 37, 2015: 73, 'matched_ids': 34},
            'school2': {2015: 8},
            'school3': {2014: 8},
            'school4': {2014: 64, 2015: 46, 'matched_ids': 55}
        }
        expected_data = [
            ['New Jersey', 'ALL', 'ALL', 'Total', 'Total', '444', '100', '555', '100', '111', '25', '0', '333', '75'],
            ['New Jersey', 'Central Regional', 'ALL', 'Total', 'Total', '123', '100', '90', '100', '-33', '-26.83', '0', '100', '81.3'],
            ['New Jersey', 'Capital Regional', 'ALL', 'Total', 'Total', '20', '100', '20', '100', '0', '0', '0', '18', '90'],
            ['New Jersey', 'Central Regional', 'Springfield Elementary', 'Total', 'Total', '37', '100', '73', '100', '36', '97.3', '0', '34', '91.89'],
            ['New Jersey', 'Central Regional', 'Springfield Junior High', 'Total', 'Total', '', '', '8', '100', '', '', '', '', ''],
            ['New Jersey', 'Capital Regional', 'Capital Charter School', 'Total', 'Total', '8', '100', '', '', '', '', '', '', ''],
            ['New Jersey', 'Capital Regional', 'Capital School Of Interpretive Dance', 'Total', 'Total', '64', '100', '46', '100', '-18', '-28.12', '0', '55', '85.94']
        ]

        data = get_tracker_results(report_map, total_tracker, trackers, 2015)

        index = 0
        for row in data:
            self.assertEquals(expected_data[index], row)
            index += 1
        self.assertEquals(7, index)
