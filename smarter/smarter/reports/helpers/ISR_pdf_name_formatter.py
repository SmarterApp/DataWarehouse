'''
Created on May 17, 2013

@author: tosako
'''
import os
from sqlalchemy.sql.expression import Select, and_
from edapi.exceptions import NotFoundException
from smarter.reports.helpers.constants import Constants
from smarter.database.smarter_connector import SmarterDBConnection


def generate_isr_report_path_by_student_guid(pdf_report_base_dir='/', student_guid=None, asmt_type=Constants.SUMMATIVE, grayScale=False):
    '''
    get report absolute path by student_guid.
    if the directroy path does not exist, then create it.
    For security, the directory will be created with only the owner can read-write.
    '''
    # find state_code, asmt_period_year, district_guid, school_guid, and asmt_grade from DB
    with SmarterDBConnection() as connection:
        fact_asmt_outcome = connection.get_table(Constants.FACT_ASMT_OUTCOME)
        dim_asmt = connection.get_table(Constants.DIM_ASMT)
        query = Select([fact_asmt_outcome.c.state_code.label(Constants.STATE_CODE),
                        dim_asmt.c.asmt_period_year.label(Constants.ASMT_PERIOD_YEAR),
                        fact_asmt_outcome.c.district_guid.label(Constants.DISTRICT_GUID),
                        fact_asmt_outcome.c.school_guid.label(Constants.SCHOOL_GUID),
                        fact_asmt_outcome.c.asmt_grade.label(Constants.ASMT_GRADE)],
                       from_obj=[fact_asmt_outcome
                                 .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_asmt_outcome.c.asmt_rec_id,
                                                      dim_asmt.c.most_recent,
                                                      dim_asmt.c.asmt_type == asmt_type))])
        query = query.where(and_(fact_asmt_outcome.c.most_recent, fact_asmt_outcome.c.status == 'C', fact_asmt_outcome.c.student_guid == student_guid))
        result = connection.get_result(query)
        if result:
            first_record = result[0]
            state_code = first_record[Constants.STATE_CODE]
            asmt_period_year = str(first_record[Constants.ASMT_PERIOD_YEAR])
            district_guid = first_record[Constants.DISTRICT_GUID]
            school_guid = first_record[Constants.SCHOOL_GUID]
            asmt_grade = first_record[Constants.ASMT_GRADE]
        else:
            raise NotFoundException("There are no results for student id {0}".format(student_guid))
    # get absolute file path name
    file_path = generate_isr_absolute_file_path_name(pdf_report_base_dir=pdf_report_base_dir, state_code=state_code, asmt_period_year=asmt_period_year, district_guid=district_guid, school_guid=school_guid, asmt_grade=asmt_grade, student_guid=student_guid, asmt_type=asmt_type, grayScale=grayScale)
    return file_path


def generate_isr_absolute_file_path_name(pdf_report_base_dir='/', state_code=None, asmt_period_year=None, district_guid=None, school_guid=None, asmt_grade=None, student_guid=None, asmt_type=Constants.SUMMATIVE, grayScale=False):
    '''
    generate isr absolute file path name
    '''
    dirname = os.path.join(pdf_report_base_dir, state_code, asmt_period_year, district_guid, school_guid, asmt_grade, 'isr', asmt_type, student_guid)
    return dirname + (".g.pdf" if grayScale else ".pdf")
