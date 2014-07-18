'''
Created on May 17, 2013

@author: tosako
'''
import os
from sqlalchemy.sql.expression import Select, and_, distinct
from edapi.exceptions import NotFoundException
from smarter.reports.helpers.constants import Constants, AssessmentType
from edcore.database.edcore_connector import EdCoreDBConnection


def generate_isr_report_path_by_student_id(state_code, effective_date=None, asmt_year=None, pdf_report_base_dir='/', student_ids=None, asmt_type=AssessmentType.SUMMATIVE, grayScale=True, lang='en'):
    '''
    Get Individual Student Report absolute path by student_id.
    If the directory path does not exist, then create it.
    For security, the directory will be created with only the owner can read-write.
    '''
    if effective_date is None and asmt_year is None:
        raise AttributeError('Need one of effective_date or asmt_year')

    file_paths = {}
    if type(student_ids) is not list:
        student_ids = [student_ids]
    # find state_code, asmt_period_year, district_id, school_id, and asmt_grade from DB
    with EdCoreDBConnection(state_code=state_code) as connection:
        fact_asmt_outcome_vw = connection.get_table(Constants.FACT_ASMT_OUTCOME_VW)
        dim_asmt = connection.get_table(Constants.DIM_ASMT)
        query = Select([distinct(fact_asmt_outcome_vw.c.student_id).label(Constants.STUDENT_ID),
                        fact_asmt_outcome_vw.c.state_code.label(Constants.STATE_CODE),
                        dim_asmt.c.asmt_period_year.label(Constants.ASMT_PERIOD_YEAR),
                        dim_asmt.c.effective_date.label(Constants.EFFECTIVE_DATE),
                        fact_asmt_outcome_vw.c.district_id.label(Constants.DISTRICT_ID),
                        fact_asmt_outcome_vw.c.school_id.label(Constants.SCHOOL_ID),
                        fact_asmt_outcome_vw.c.asmt_grade.label(Constants.ASMT_GRADE)],
                       from_obj=[fact_asmt_outcome_vw
                                 .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_asmt_outcome_vw.c.asmt_rec_id,
                                                      dim_asmt.c.rec_status == Constants.CURRENT,
                                                      dim_asmt.c.asmt_type == asmt_type))])
        query = query.where(and_(fact_asmt_outcome_vw.c.rec_status == Constants.CURRENT, fact_asmt_outcome_vw.c.student_id.in_(student_ids)))
        if effective_date is not None:
            query = query.where(and_(dim_asmt.c.effective_date == effective_date))
        elif asmt_year is not None:
            query = query.where(and_(dim_asmt.c.asmt_period_year == asmt_year))
        results = connection.get_result(query)
        if len(results) != len(student_ids):
            raise NotFoundException("student count does not match with result count")
        for result in results:
            student_id = result[Constants.STUDENT_ID]
            state_code = result[Constants.STATE_CODE]
            asmt_period_year = str(result[Constants.ASMT_PERIOD_YEAR])
            effective_date = str(result[Constants.EFFECTIVE_DATE])
            district_id = result[Constants.DISTRICT_ID]
            school_id = result[Constants.SCHOOL_ID]
            asmt_grade = result[Constants.ASMT_GRADE]

            # get absolute file path name
            file_path = generate_isr_absolute_file_path_name(pdf_report_base_dir=pdf_report_base_dir, state_code=state_code, asmt_period_year=asmt_period_year, district_id=district_id, school_id=school_id, asmt_grade=asmt_grade, student_id=student_id, asmt_type=asmt_type, grayScale=grayScale, lang=lang, effective_date=effective_date)
            file_paths[student_id] = file_path
    return file_paths


def generate_isr_absolute_file_path_name(pdf_report_base_dir='/', state_code=None, asmt_period_year=None, district_id=None, school_id=None, asmt_grade=None, student_id=None, asmt_type=AssessmentType.SUMMATIVE, grayScale=False, lang='en', effective_date=None):
    '''
    Generate Individual Student Report absolute file path name
    '''
    dirname = os.path.join(pdf_report_base_dir, state_code, asmt_period_year, district_id, school_id, asmt_grade, 'isr', asmt_type, student_id + '.' + effective_date + '.' + lang)
    return dirname + (".g.pdf" if grayScale else ".pdf")
