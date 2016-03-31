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
from smarter_score_batcher.utils.xml_utils import extract_meta_with_fallback_helper
from smarter_score_batcher.utils.xml_utils import extract_meta_without_fallback_helper
from edapi.httpexceptions import EdApiHTTPPreconditionFailed
import logging
import os
from smarter_score_batcher.error.exceptions import MetaNamesException
import re
from smarter_score_batcher.celery import conf
from edauth.security.utils import load_class

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


logger = logging.getLogger("smarter_score_batcher")


class Meta:
    '''
    Object to hold parts of the folder structure
    '''
    def __init__(self, valid_meta, student_id, state_code, district_id, academic_year, asmt_type, subject, grade, effective_date, asmt_id):
        if effective_date:
            m = re.search('(\d+)-(\d+)-(\d+)', effective_date)
            if m:
                effective_date = m.group(1) + m.group(2) + m.group(3)
        self.__student_id = student_id
        self.__state_code = state_code
        self.__district_id = district_id
        self.__academic_year = academic_year
        self.__asmt_type = asmt_type
        self.__grade = grade
        self.__subject = subject
        self.__effective_date = effective_date
        self.__asmt_id = asmt_id
        self.__valid_meta = valid_meta

    @property
    def student_id(self):
        return self.__student_id

    @property
    def state_code(self):
        return self.__state_code

    @property
    def district_id(self):
        return self.__district_id

    @property
    def academic_year(self):
        return self.__academic_year

    @property
    def asmt_type(self):
        return self.__asmt_type.upper() if self.__asmt_type is not None else None

    @property
    def grade(self):
        return self.__grade

    @property
    def subject(self):
        return self.__subject

    @property
    def effective_date(self):
        return self.__effective_date

    @property
    def asmt_id(self):
        return self.__asmt_id

    @property
    def valid_meta(self):
        return self.__valid_meta

    @property
    def test_label(self):
        return None


def extract_meta_names(raw_xml_string):
    '''
    Validates and extracts meta from the XML.
    Returns: True if meta for file path is valid. And the parts for folder creation.
    :param raw_xml_string: xml data
    '''
    try:
        root = ET.fromstring(raw_xml_string)
        state_code = extract_meta_with_fallback_helper(root, "./Examinee/ExamineeRelationship/[@name='StateAbbreviation']", "value", "context")
        student_id = extract_meta_with_fallback_helper(root, "./Examinee/ExamineeAttribute/[@name='StudentIdentifier']", "value", "context")
        district_id = extract_meta_with_fallback_helper(root, "./Examinee/ExamineeRelationship/[@name='ResponsibleDistrictIdentifier']", "value", "context")
        academic_year = extract_meta_without_fallback_helper(root, "./Test", "academicYear")
        asmt_type = extract_meta_without_fallback_helper(root, "./Test", "assessmentType")
        subject = extract_meta_without_fallback_helper(root, "./Test", "subject")
        grade = extract_meta_without_fallback_helper(root, "./Test", "grade")
        effective_date = extract_meta_without_fallback_helper(root, "./Opportunity", "dateCompleted")

        # Get asmt id, not required for validation
        asmt_id = extract_meta_without_fallback_helper(root, "./Test", "testId")
        validMeta = (state_code and student_id and district_id and academic_year and asmt_type and subject and grade and effective_date)
        if not validMeta:
            error_msg = ''
            if not state_code:
                error_msg += os.linesep + 'extract_meta_names: state_code is missing'
            if not student_id:
                error_msg += os.linesep + 'extract_meta_names: student_id is missing'
            if not district_id:
                error_msg += os.linesep + 'extract_meta_names: district_id is missing'
            if not academic_year:
                error_msg += os.linesep + 'extract_meta_names: academic_year is missing'
            if not asmt_type:
                error_msg += os.linesep + 'extract_meta_names: asmt_type is missing'
            if not subject:
                error_msg += os.linesep + 'extract_meta_names: subject is missing'
            if not grade:
                error_msg += os.linesep + 'extract_meta_names: grade is missing'
            if not effective_date:
                error_msg += os.linesep + 'extract_meta_names: effective_date is missing'
            logger.error(error_msg)
            raise MetaNamesException(error_msg)
        meta_class = load_class(conf.get('smarter_score_batcher.class.meta', 'smarter_score_batcher.utils.meta.Meta'))
        return meta_class(validMeta, student_id, state_code, district_id, academic_year, asmt_type, subject, grade, effective_date, asmt_id)
    except ET.ParseError:
        raise EdApiHTTPPreconditionFailed("Invalid XML")
