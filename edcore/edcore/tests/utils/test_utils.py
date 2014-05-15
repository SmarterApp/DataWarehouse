'''
Created on Sep 1, 2013

@author: dip
'''
import unittest
from edcore.utils.utils import merge_dict, delete_multiple_entries_from_dictionary_by_list_of_keys,\
    reverse_map


class TestUtils(unittest.TestCase):

    def test_merge_dict(self):
        self.assertDictEqual(merge_dict({}, {}), {})
        self.assertDictEqual(merge_dict({'a': 'b'}, {'c': 'd'}),
                             {'a': 'b', 'c': 'd'})
        self.assertDictEqual(merge_dict({'a': 'b'}, {'a': 'd'}), {'a': 'b'})

    def test_delete_multiple_entries_from_dictionary_by_list_of_keys(self):
        self.assertDictEqual(delete_multiple_entries_from_dictionary_by_list_of_keys({}, ['a']), {})
        self.assertDictEqual(delete_multiple_entries_from_dictionary_by_list_of_keys({'a': 1}, 'b'), {'a': 1})
        self.assertDictEqual(delete_multiple_entries_from_dictionary_by_list_of_keys({'a': 1}, 'a'), {})

    def test_reverse_map(self):
        _map = {'a': 'b', 'c': 'd'}
        reverse = reverse_map(_map)
        self.assertEqual(reverse['b'], 'a')

    def test_reverse_empty(self):
        _map = {}
        reverse = reverse_map(_map)
        self.assertEqual(len(reverse.keys()), 0)

if __name__ == "__main__":
    unittest.main()
