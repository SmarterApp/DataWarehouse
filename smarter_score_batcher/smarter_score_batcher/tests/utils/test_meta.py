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

'''
Created on Aug 12, 2014

@author: tosako
'''
import unittest
from edapi.httpexceptions import EdApiHTTPPreconditionFailed
from smarter_score_batcher.utils.meta import extract_meta_names
from smarter_score_batcher.error.exceptions import TSBException


class Test(unittest.TestCase):

    def test_extract_meta_names_empty_xml(self):
        xml_string = ''
        self.assertRaises(EdApiHTTPPreconditionFailed, extract_meta_names, xml_string)

    def test_extract_meta_names_incomplete_xml(self):
        xml_string = '<xml></xml>'
        self.assertRaises(TSBException, extract_meta_names, xml_string)

    def test_extract_meta_names_valid_minimum_xml(self):
        xml_string = '''<TDSReport>
        <Test subject="MA" grade="3-12" assessmentType="Formative" academicYear="2014" />
        <Examinee key="CA-9999999598-11">
        <ExamineeRelationship context="FINAL" name="ResponsibleDistrictIdentifier" value="CA_9999827" />
        <ExamineeRelationship context="FINAL" name="StateName" value="California" />
        <ExamineeRelationship context="INITIAL" name="ResponsibleDistrictIdentifier" value="CA_9999827" />
        <ExamineeRelationship context="INITIAL" name="StateAbbreviation" value="California" />
        <ExamineeAttribute context="INITIAL" name="StudentIdentifier" value="CA-9999999598" />
        </Examinee>
        <Opportunity dateCompleted="2014-02-02T16:12:24.238" />
        </TDSReport>'''
        meta = extract_meta_names(xml_string)
        self.assertTrue(meta.valid_meta)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
