__author__ = 'swimberly'

import unittest
import pwd
import os
import shutil
import tempfile

from edsftp.src.initialize_sftp_user import delete_user,\
    _verify_user_tenant_and_group, get_user_path,\
    get_user_role_dir, get_user_home_dir, get_user_sftp_jail_dir
from edsftp.src.configure_sftp_groups import cleanup as clean_group
from edsftp.src.initialize_sftp_tenant import remove_tenant
from edsftp.src.util import create_path


class TestInitSFTPUser(unittest.TestCase):

    def setUp(self):
        self.__temp_dir = tempfile.mkdtemp()
        self.sftp_conf = {
            'sftp_home': self.__temp_dir,
            'sftp_base_dir': 'sftp/opt/edware/home',
            'sftp_arrivals_dir': 'arrivals',
            'sftp_departures_dir': 'departures',
            'sftp_filerouter_dir': '',
            'group': 'testgroup',
            'roles': ['sftparrivals', 'sftpdepartures', 'filerouter'],
            'user_path_sftparrivals_dir': 'tst_file_drop',
            'user_path_sftpdepartures_dir': 'reports',
            'user_path_filerouter_dir': 'route',
            'user_home_base_dir': '/opt/edware/home',
        }
        self.user_dels = []
        self.tenant_dels = []
        self.del_groups = False

    def tearDown(self):
        for user in self.user_dels:
            delete_user(user, self.sftp_conf)
        for tenant in self.tenant_dels:
            remove_tenant(tenant, self.sftp_conf)
        if self.del_groups:
            clean_group(self.sftp_conf)
        shutil.rmtree(self.__temp_dir, ignore_errors=True)

    def test_verify_user_tenant_and_role_tenant_path(self):
        home_folder = os.path.join(self.__temp_dir, 'does_not_exist')
        expected_result = (False, 'Tenant does not exist!')
        result = _verify_user_tenant_and_group(home_folder, 'test_user', 'group', 'some_role')

        self.assertEqual(expected_result, result)

    def test_verify_user_tenant_and_role__role(self):
        tenant_folder = os.path.join(self.__temp_dir, 'test_does_exist')
        create_path(tenant_folder)
        expected_result = (False, 'Group does not exist as a group in the system')
        result = _verify_user_tenant_and_group(tenant_folder, 'some_user', 'gddroup', 'made_up_role')

        self.assertEqual(result, expected_result)

    def test_verify_user_tenant_and_role__user(self):
        tenant_folder = os.path.join(self.__temp_dir, 'test_does_exist')
        create_path(tenant_folder)

        expected_result = (False, 'Group does not exist as a group in the system')
        result = _verify_user_tenant_and_group(tenant_folder, 'root', 'invalidGroup', 'wheel')

        self.assertEqual(expected_result, result)

    def test_verify_user_tenant_and_role__valid_input(self):
        tenant_folder = os.path.join(self.__temp_dir, 'test_does_exist')
        create_path(tenant_folder)

        expected_result = True, ""
        result = _verify_user_tenant_and_group(tenant_folder, 'the_roots', 'wheel', 'wheel')

        self.assertEqual(expected_result, result)

#    def test__set_ssh_key_exists(self):
#        create_path('/tmp/test_sftp_user')
#        self.cleanup_dirs.append('/tmp/test_sftp_user')
#
#        public_key_str = "blahblahblahblahblah" * 20
#        _set_ssh_key('test_sftp_user', 'testgrp1', '/tmp/test_sftp_user', public_key_str)
#        self.assertTrue(os.path.exists('/tmp/test_sftp_user/.ssh/authorized_keys'))
#
#    def test__set_ssh_key(self):
#        create_path('/tmp/test_sftp_user')
#        init_group(self.sftp_conf)
#        self.cleanup_dirs.append('/tmp/test_sftp_user')
#
#        public_key_str = "blahblahblahblahblah" * 20
#        _set_ssh_key('test_sftp_user', 'testgrp1', '/tmp/test_sftp_user', public_key_str)
#        with open('/tmp/test_sftp_user/.ssh/authorized_keys') as key_file:
#            public_key_str += '\n'
#            self.assertEqual(key_file.read(), public_key_str)
#
#        self.del_groups = True

    def check_user_does_not_exist(self, user):
        with self.assertRaises(KeyError):
            pwd.getpwnam(user)

    def test_get_user_path_arrivals(self):
        path = get_user_path(self.sftp_conf, "sftparrivals")
        self.assertEqual(path, self.sftp_conf["user_path_sftparrivals_dir"])

    def test_get_user_path_dept(self):
        path = get_user_path(self.sftp_conf, "sftpdepartures")
        self.assertEqual(path, self.sftp_conf["user_path_sftpdepartures_dir"])

    def test_get_user_path_filerouters(self):
        path = get_user_path(self.sftp_conf, "filerouter")
        self.assertEqual(path, self.sftp_conf["user_path_filerouter_dir"])

    def test_get_user_role_dir_arrivals(self):
        _dir = get_user_role_dir(self.sftp_conf, 'sftparrivals')
        self.assertEqual(_dir, self.sftp_conf["sftp_arrivals_dir"])

    def test_get_user_role_dir_departures(self):
        _dir = get_user_role_dir(self.sftp_conf, 'sftpdepartures')
        self.assertEqual(_dir, self.sftp_conf["sftp_departures_dir"])

    def test_get_user_role_dir_filerouter(self):
        _dir = get_user_role_dir(self.sftp_conf, 'filerouter')
        self.assertEqual(_dir, self.sftp_conf["sftp_filerouter_dir"])

    def test_get_user_home_dir_arrivals(self):
        path = get_user_home_dir(self.sftp_conf, 'tenant', 'user', 'sftparrivals')
        self.assertEqual(path, '/opt/edware/home/arrivals/tenant/user')

    def test_get_user_home_dir_departures(self):
        path = get_user_home_dir(self.sftp_conf, 'tenant', 'user', 'sftpdepartures')
        self.assertEqual(path, '/opt/edware/home/departures/tenant/user')

    def test_get_user_home_dir_filerouter(self):
        path = get_user_home_dir(self.sftp_conf, 'tenant', 'user', 'filerouter')
        self.assertEqual(path, '/opt/edware/home/user')

    def test_get_user_sftp_jail_dir_arrivals(self):
        path = get_user_sftp_jail_dir(self.sftp_conf, 'tenant', 'user', 'sftparrivals')
        self.assertEqual(path, os.path.join(self.__temp_dir, 'sftp/opt/edware/home', 'arrivals', 'tenant', 'user'))

    def test_get_user_sftp_jail_dir_departures(self):
        path = get_user_sftp_jail_dir(self.sftp_conf, 'tenant', 'user', 'sftpdepartures')
        self.assertEqual(path, os.path.join(self.__temp_dir, 'sftp/opt/edware/home', 'departures', 'tenant', 'user'))

    def test_get_user_sftp_jail_dir_filerouter(self):
        path = get_user_sftp_jail_dir(self.sftp_conf, 'tenant', 'user', 'filerouter')
        self.assertEqual(path, os.path.join(self.__temp_dir, 'sftp/opt/edware/home', 'user'))

if __name__ == '__main__':
    unittest.main()
