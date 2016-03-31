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

import tempfile
import shutil
__author__ = 'sravi'

import unittest
import os
import time
from uuid import uuid4
from edudl2.udl2.defaults import UDL2_DEFAULT_CONFIG_PATH_FILE
import edudl2.udl2.message_keys as mk
from edudl2.post_etl import post_etl
from edudl2.udl2_util.config_reader import read_ini_file


class TestPostEtl(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        try:
            config_path = dict(os.environ)['UDL2_CONF']
        except Exception:
            config_path = UDL2_DEFAULT_CONFIG_PATH_FILE
        conf_tup = read_ini_file(config_path)
        self.conf = conf_tup[0]

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(self):
        pass

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _get_mock_tenant(self):
        return 'ca'

    def _get_mock_work_zone_directory(self):
        return time.strftime('%Y%m%d%H%M%S', time.gmtime()) + '_' + str(uuid4())

    def _set_up_mock_work_zone(self, directory_dict):
        for directory in directory_dict.values():
            os.makedirs(directory, mode=0o777)
            open(os.path.join(directory, 'test_file.txt'), 'a').close()

    def test_work_zone_cleaned_up_completely(self):
        tenant_name = self._get_mock_tenant()
        dir_name = self._get_mock_work_zone_directory()

        work_zone_directories_to_cleanup = {
            mk.ARRIVED: os.path.join(self.temp_dir, tenant_name, 'arrived', dir_name),
            mk.DECRYPTED: os.path.join(self.temp_dir, tenant_name, 'decrypted', dir_name),
            mk.EXPANDED: os.path.join(self.temp_dir, tenant_name, 'expanded', dir_name),
            mk.SUBFILES: os.path.join(self.temp_dir, tenant_name, 'subfiles', dir_name),
        }
        self._set_up_mock_work_zone(work_zone_directories_to_cleanup)
        self.assertTrue(post_etl.cleanup_work_zone(work_zone_directories_to_cleanup))
        self.assertFalse(os.path.exists(work_zone_directories_to_cleanup[mk.ARRIVED]))
        self.assertFalse(os.path.exists(work_zone_directories_to_cleanup[mk.DECRYPTED]))
        self.assertFalse(os.path.exists(work_zone_directories_to_cleanup[mk.EXPANDED]))
        self.assertFalse(os.path.exists(work_zone_directories_to_cleanup[mk.SUBFILES]))
