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

import logging
import unittest
from pyramid.testing import DummyRequest
from pyramid import testing
from hpz.frs import registration_service
from hpz.frs.registration_service import put_file_registration_service
from pyramid.registry import Registry
import json
from unittest import mock
from unittest.mock import patch

__author__ = 'npandey'


class RegistrationTest(unittest.TestCase):

    def setUp(self):
        self.__request = DummyRequest()
        reg = Registry()
        reg.settings = {'hpz.frs.download_base_url': 'http://blah/download'}
        self.__config = testing.setUp(registry=reg, request=self.__request, hook_zca=False)
        self.__config.add_route('download', '/{reg_id}')

    def tearDown(self):
        self.__request = None

    @patch('hpz.frs.registration_service.FileRegistry.register_request')
    def test_registration(self, persist_patch):

        persist_patch.return_value = None

        self.__request.method = 'PUT'
        self.__request.json_body = {'uid': '1234', 'email': 'foo@foo.com'}

        response = put_file_registration_service(None, self.__request)

        self.assertEqual(response.status_code, 200)

        response_json = json.loads(str(response.body, encoding='UTF-8'))

        self.assertTrue('url' in response_json)
        self.assertTrue('registration_id' in response_json)
        registration_id = response_json['registration_id']
        self.assertEqual('http://blah/files/' + registration_id, response_json['url'])
        persist_patch.assert_called_with('1234', 'foo@foo.com')

    @patch('hpz.frs.registration_service.FileRegistry.register_request')
    def test_registration_valid_url(self, persist_patch):
        reg = Registry()
        reg.settings = {'hpz.frs.download_base_url': 'http://blah/download'}
        self.__config = testing.setUp(registry=reg, request=self.__request, hook_zca=False)

        persist_patch.return_value = None

        self.__request.method = 'PUT'
        self.__request.json_body = {'uid': '1234', 'email': 'foo@foo.com'}

        response = put_file_registration_service(None, self.__request)

        self.assertEqual(response.status_code, 200)

        response_json = json.loads(str(response.body, encoding='UTF-8'))

        self.assertTrue('url' in response_json)
        self.assertTrue('registration_id' in response_json)
        registration_id = response_json['registration_id']
        self.assertEqual('http://blah/files/' + registration_id, response_json['url'])

    @patch('hpz.frs.registration_service.FileRegistry.register_request')
    def test_registration_incorrect_payload(self, persist_patch):
            persist_patch.return_value = None

            self.__request.method = 'PUT'
            self.__request.json_body = {}

            response = put_file_registration_service(None, self.__request)

            self.assertEqual(response.status_code, 200)

            response_json = json.loads(str(response.body, encoding='UTF-8'))
            self.assertTrue('url' not in response_json)
            self.assertTrue(not persist_patch.called)
