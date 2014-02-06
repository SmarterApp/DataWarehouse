__author__ = 'sravi'

import unittest
import collections
import edmigrate.nodes.nodes as nodes


class TesNodes(unittest.TestCase):

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    def tearDown(self):
        pass

    def test_dummy(self):
        pass

    def test_slave_node_host_names_for_group(self):
        node = collections.namedtuple('node', 'host group')
        test_registered_slaves = []
        test_registered_slaves.append(node(host='testslave0.qa.dum.edwdc.net', group='A'))
        test_registered_slaves.append(node(host='testslave1.qa.dum.edwdc.net', group='B'))
        self.assertTrue(len(nodes.get_slave_node_host_names_for_group('A', test_registered_slaves)) == 1)


if __name__ == "__main__":
    unittest.main()
