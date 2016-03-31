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

import os
import shutil
import unittest
from edudl2.udl2.defaults import UDL2_DEFAULT_CONFIG_PATH_FILE
from edudl2.udl2_util.config_reader import read_ini_file
from edudl2.tests.utils.encrypt_helper import EncryptHelper


class UDLTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls, data_dir):
        try:
            config_path_file = os.environ['UDL2_CONF']
        except Exception:
            config_path_file = UDL2_DEFAULT_CONFIG_PATH_FILE

        cls.udl2_conf, cls.settings = read_ini_file(config_path_file)
        cls.encrypt_helper = EncryptHelper(cls.settings)
        cls.data_dir = data_dir
        cls.gpg_home = cls.settings.get('gpg_home', None)
        # prepare gpg keys for tests
        if cls.gpg_home and not os.path.exists(cls.gpg_home):
            config_gpg = os.path.join(os.path.dirname(__file__), "../../../../config/gpg")
            shutil.copytree(config_gpg, cls.gpg_home)

    @classmethod
    def tearDownClass(cls):
        pass

    @classmethod
    def require_gpg_file(cls, dir_path):
        data_path = os.path.join(cls.data_dir, dir_path)
        return cls.encrypt_helper.create_gpg(data_path)

    @classmethod
    def require_gpg_checksum(cls, dir_path):
        data_path = os.path.join(cls.data_dir, dir_path)
        return cls.encrypt_helper.create_gpg_and_checksum(data_path)

    @classmethod
    def require_tar_file(cls, dir_path):
        data_path = os.path.join(cls.data_dir, dir_path)
        return cls.encrypt_helper.compress_directory(data_path)

    @classmethod
    def require_file(cls, dir_path):
        return os.path.join(cls.data_dir, dir_path)
