# (c) 2014 The Regents of the University of California. All rights reserved,
# subject to the license below.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0. Unless required by
# applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

import unittest
from pyramid import testing
from pyramid.registry import Registry
from pyramid.testing import DummyRequest
from smarter_score_batcher.celery import setup_celery
from unittest.mock import patch
import os
import tempfile
from smarter_score_batcher.services.xml import xml_catcher
from smarter_score_batcher.tests.database.unittest_with_tsb_sqlite import Unittest_with_tsb_sqlite
from pyramid.httpexceptions import HTTPServiceUnavailable
here = os.path.abspath(os.path.dirname(__file__))
xsd_file_path = os.path.abspath(os.path.join(here, '..', '..', '..', 'resources', 'sample_xsd.xsd'))


class TestXML(Unittest_with_tsb_sqlite):

    def setUp(self):
        self.__tempfolder = tempfile.TemporaryDirectory()
        # setup request
        self.__request = DummyRequest()
        self.__request.method = 'POST'
        # setup registry
        settings = {
            'smarter_score_batcher.celery_timeout': 30,
            'smarter_score_batcher.celery.celery_always_eager': True
        }
        reg = Registry()
        reg.settings = settings
        self.__config = testing.setUp(registry=reg, request=self.__request, hook_zca=False)
        setup_celery(settings, db_connection=False)

    def tearDown(self):
        testing.tearDown()

    @patch('smarter_score_batcher.services.xml.process_xml')
    def test_xml_catcher_succeed(self, mock_process_xml):
        mock_process_xml.return_value = True
        self.__request.body = '<xml></xml>'
        response = xml_catcher(self.__request)
        self.assertEqual(response.status_code, 202, "should return 200 after writing xml file")

    @patch('smarter_score_batcher.services.xml.process_xml')
    def test_xml_catcher_failed(self, mock_process_xml):
        mock_process_xml.return_value = False
        self.__request.body = '<xml></xml>'
        response = xml_catcher(self.__request)
        self.assertEqual(type(HTTPServiceUnavailable()), type(response))

    @patch('smarter_score_batcher.services.xml.process_xml')
    def test_xml_catcher_no_content(self, mock_process_xml):
        mock_process_xml.side_effect = Exception()
        self.__request.body = ''
        self.assertRaises(Exception, xml_catcher, self.__request)


if __name__ == '__main__':
    unittest.main()
