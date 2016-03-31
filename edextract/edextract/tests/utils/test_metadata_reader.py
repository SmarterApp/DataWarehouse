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

'''
Created on Jul 22, 2014

@author: tosako
'''
import unittest
import tempfile
import os
from edextract.utils.metadata_reader import MetadataReader


class Test(unittest.TestCase):

    def setUp(self):
        self.__temp_dir = tempfile.mkdtemp()
        self.__dir11 = os.path.join(self.__temp_dir, 'dir1', 'dir1-1')
        self.__dir21 = os.path.join(self.__temp_dir, 'dir2', 'dir2-1')
        os.makedirs(self.__dir11, exist_ok=True)
        os.makedirs(self.__dir21, exist_ok=True)
        self.file1 = os.path.join(self.__dir11, 'hello1')
        self.file2 = os.path.join(self.__dir11, 'hello2')
        self.file3 = os.path.join(self.__dir11, 'hello3')
        self.file4 = os.path.join(self.__dir21, 'hello4')

        with open(self.file1, 'w') as f:
            f.write('hello world')
        with open(self.file2, 'w') as f:
            f.write('good bye world')
        with open(self.file3, 'w') as f:
            f.write('good morning world')
        with open(self.file4, 'w') as f:
            f.write('abc')
        with open(os.path.join(self.__dir11, '.metadata'), 'w') as f:
            f.write('f:hello1:11:111111\n')
            f.write('f:hello3:18:111111')

    def test_get_size_from_metadata(self):
        metadata = MetadataReader()
        size = metadata.get_size(self.file1)
        self.assertEqual(11, size)
        size = metadata.get_size(self.file3)
        self.assertEqual(18, size)

    def test_get_size_from_disk(self):
        metadata = MetadataReader()
        size = metadata.get_size(self.file2)
        self.assertEqual(14, size)

    def test_get_size_no_metadata(self):
        metadata = MetadataReader()
        size = metadata.get_size(self.file4)
        self.assertEqual(3, size)

    def test_get_files(self):
        metadata = MetadataReader()
        files = metadata.get_files(os.path.join(self.__dir11, 'hello*'))
        self.assertEqual(2, len(files))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
