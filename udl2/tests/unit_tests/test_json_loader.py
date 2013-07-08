'''
Created on May 17, 2013

@author: swimberly
'''

import fileloader.json_loader as jload
import json
import os
import unittest


class TestJsonLoader(unittest.TestCase):

    def setUp(self):
        self.json_dict = {'pls': {'pl1': {'cp': '1200', 'name': 'Minimal', 'level': 1}, 'pl2': {'cp': '1400', 'name': 'Partial', 'level': 2},
                                  'pl3': {'cp': '1800', 'name': 'Adequate', 'level': 3}},
                          'id': {'year': '2015', 'id': '28', 'subject': 'Math', 'period': '2015', 'type': 'SUMMATIVE', 'version': 'V1'}
                          }
        self.mappings = {'val1': ['pls', 'pl1', 'name'], 'val2': ['pls', 'pl2', 'name'], 'val3': ['pls', 'pl3', 'name'], 'val4': ['pls', 'pl2', 'level'],
                        'val5': ['id', 'year'], 'val6': ['id', 'type'], 'val7': ['pls', 'pl3', 'cp'], 'val8': ['pls', 'pl1', 'level']
                        }

    def test_flatten_json_dict(self):
        expected = {'val1': 'Minimal',
                    'val2': 'Partial',
                    'val3': 'Adequate',
                    'val4': 2,
                    'val5': '2015',
                    'val6': 'SUMMATIVE',
                    'val7': '1800',
                    'val8': 1
                    }
        result = jload.flatten_json_dict(self.json_dict, self.mappings)

        self.assertEqual(expected, result)

    def test_read_json_file(self):
        with open('test_read_json_file.json', 'w') as jf:
            json.dump(self.json_dict, jf, indent=4)
        result = jload.read_json_file('test_read_json_file.json')
        self.assertEqual(result, self.json_dict)
        os.remove('test_read_json_file.json')

    def test_fix_empty_strings_1(self):
        ''' check method with no empty strings in dict '''
        data_dict = {'a': '1', 'b': '2', 'c': '3'}
        res_dict = jload.fix_empty_strings(data_dict)
        self.assertEqual(data_dict, res_dict, 'no changes should have been made to the dict')

    def test_fix_empty_string_2(self):
        ''' check with some empty strings '''
        data_dict = {'a': '', 'b': '2', 'c': "", 'd': 0, 'e': '0'}
        expected = {'a': None, 'b': '2', 'c': None, 'd': 0, 'e': '0'}
        res = jload.fix_empty_strings(data_dict)
        self.assertEqual(res, expected, 'Check with a few empty strings')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
