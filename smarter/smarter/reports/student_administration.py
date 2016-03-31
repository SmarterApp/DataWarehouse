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
Created on Jan 13, 2013
'''
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import and_, distinct
from edapi.cache import cache_region
from edcore.database.edcore_connector import EdCoreDBConnection
from smarter.reports.helpers.constants import Constants, AssessmentType
from edcore.database.routing import ReportingDbConnection

DEFAULT_YEAR_BACK = 1


def get_asmt_administration_years(state_code, district_id=None, school_id=None, asmt_grade=None, student_ids=None, asmt_year=None):
    return get_asmt_administration(state_code, district_id, school_id, asmt_grade, student_ids, asmt_year) +\
        get_block_asmt_administration(state_code, district_id, school_id, asmt_grade, student_ids, asmt_year)


def get_asmt_administration_years_isr(state_code, district_id=None, school_id=None, asmt_grade=None, student_ids=None, asmt_year=None):
    return get_asmt_administration_isr(state_code, district_id, school_id, asmt_grade, student_ids, asmt_year) +\
        get_block_asmt_administration(state_code, district_id, school_id, asmt_grade, student_ids, asmt_year)


def get_asmt_administration_isr(state_code, district_id=None, school_id=None, asmt_grade=None, student_ids=None, asmt_year=None):
    '''
    Get asmt administration for individual student report. There is no PII in the results and it can be stored in shortlived cache
    '''
    with EdCoreDBConnection(state_code=state_code) as connection:
        fact_asmt_outcome_vw = connection.get_table(Constants.FACT_ASMT_OUTCOME_VW)
        dim_asmt = connection.get_table(Constants.DIM_ASMT)
        query = select([fact_asmt_outcome_vw.c.date_taken, dim_asmt.c.asmt_period_year, fact_asmt_outcome_vw.c.asmt_type, fact_asmt_outcome_vw.c.asmt_grade],
                       from_obj=[fact_asmt_outcome_vw, dim_asmt])
        query = query.where(fact_asmt_outcome_vw.c.asmt_rec_id == dim_asmt.c.asmt_rec_id).\
            where(fact_asmt_outcome_vw.c.state_code == state_code).\
            where(and_(fact_asmt_outcome_vw.c.rec_status == Constants.CURRENT)).\
            where(and_(fact_asmt_outcome_vw.c.asmt_type.in_([AssessmentType.SUMMATIVE, AssessmentType.INTERIM_COMPREHENSIVE]))).\
            group_by(fact_asmt_outcome_vw.c.date_taken, dim_asmt.c.asmt_period_year, fact_asmt_outcome_vw.c.asmt_type, fact_asmt_outcome_vw.c.asmt_grade,).\
            order_by(fact_asmt_outcome_vw.c.asmt_type.desc(), dim_asmt.c.asmt_period_year.desc())
        if district_id:
            query = query.where(and_(fact_asmt_outcome_vw.c.district_id == district_id))
        if school_id:
            query = query.where(and_(fact_asmt_outcome_vw.c.school_id == school_id))
        if asmt_grade:
            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_grade == asmt_grade))
        if student_ids:
            query = query.where(and_(fact_asmt_outcome_vw.c.student_id.in_(student_ids))) if isinstance(student_ids, list) else query.where(and_(fact_asmt_outcome_vw.c.student_id == student_ids))
        if asmt_year:
            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_year == asmt_year))
        results = connection.get_result(query)
    return results


def get_asmt_administration(state_code, district_id=None, school_id=None, asmt_grade=None, student_ids=None, asmt_year=None):
    '''
    Get asmt administration for a list of students. There is no PII in the results and it can be stored in shortlived cache
    '''
    with EdCoreDBConnection(state_code=state_code) as connection:
        fact_asmt_outcome_vw = connection.get_table(Constants.FACT_ASMT_OUTCOME_VW)
        dim_asmt = connection.get_table(Constants.DIM_ASMT)
        query = select([dim_asmt.c.asmt_period_year, fact_asmt_outcome_vw.c.asmt_type, fact_asmt_outcome_vw .c.asmt_grade],
                       from_obj=[fact_asmt_outcome_vw, dim_asmt])
        query = query.where(fact_asmt_outcome_vw.c.asmt_rec_id == dim_asmt.c.asmt_rec_id).\
            where(fact_asmt_outcome_vw.c.state_code == state_code).\
            where(and_(fact_asmt_outcome_vw.c.rec_status == Constants.CURRENT)).\
            where(and_(fact_asmt_outcome_vw.c.asmt_type.in_([AssessmentType.SUMMATIVE, AssessmentType.INTERIM_COMPREHENSIVE]))).\
            group_by(dim_asmt.c.asmt_period_year, fact_asmt_outcome_vw.c.asmt_type, fact_asmt_outcome_vw.c.asmt_grade,).\
            order_by(fact_asmt_outcome_vw.c.asmt_type.desc(), dim_asmt.c.asmt_period_year.desc())
        if district_id:
            query = query.where(and_(fact_asmt_outcome_vw.c.district_id == district_id))
        if school_id:
            query = query.where(and_(fact_asmt_outcome_vw.c.school_id == school_id))
        if asmt_grade:
            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_grade == asmt_grade))
        if student_ids:
            query = query.where(and_(fact_asmt_outcome_vw.c.student_id.in_(student_ids))) if isinstance(student_ids, list) else query.where(and_(fact_asmt_outcome_vw.c.student_id == student_ids))
        if asmt_year:
            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_year == asmt_year))
        results = connection.get_result(query)
    return results


def get_block_asmt_administration(state_code, district_id=None, school_id=None, asmt_grade=None, student_ids=None, asmt_year=None):
    '''
    Block assessment administration years
    '''
    with EdCoreDBConnection(state_code=state_code) as connection:
        fact_block_asmt = connection.get_table(Constants.FACT_BLOCK_ASMT_OUTCOME)
        dim_asmt = connection.get_table(Constants.DIM_ASMT)
        query = select([dim_asmt.c.asmt_period_year, fact_block_asmt.c.asmt_type],
                       from_obj=[fact_block_asmt, dim_asmt])
        query = query.where(fact_block_asmt.c.asmt_rec_id == dim_asmt.c.asmt_rec_id).\
            where(fact_block_asmt.c.state_code == state_code).\
            where(and_(fact_block_asmt.c.asmt_type == AssessmentType.INTERIM_ASSESSMENT_BLOCKS)).\
            where(and_(fact_block_asmt.c.rec_status == Constants.CURRENT)).\
            group_by(dim_asmt.c.asmt_period_year, fact_block_asmt.c.asmt_type)
        if district_id:
            query = query.where(and_(fact_block_asmt.c.district_id == district_id))
        if school_id:
            query = query.where(and_(fact_block_asmt.c.school_id == school_id))
        if asmt_grade:
            query = query.where(and_(fact_block_asmt.c.asmt_grade == asmt_grade))
        if student_ids:
            query = query.where(and_(fact_block_asmt.c.student_id.in_(student_ids))) if isinstance(student_ids, list) else query.where(and_(fact_block_asmt.c.student_id == student_ids))
        if asmt_year:
            query = query.where(and_(fact_block_asmt.c.asmt_year == asmt_year))
        results = connection.get_result(query)
    return results


@cache_region('public.very_shortlived')
def get_asmt_academic_years(state_code, tenant=None, years_back=None, is_public=False):
    '''
    Gets academic years.
    '''
    if not years_back or years_back <= 0:
        years_back = DEFAULT_YEAR_BACK
    with ReportingDbConnection(tenant=tenant, state_code=state_code, is_public=is_public) as connection:
        dim_asmt = connection.get_table(Constants.DIM_ASMT)
        query = select([dim_asmt.c.asmt_period_year]).distinct().order_by(dim_asmt.c.asmt_period_year.desc())
        results = connection.execute(query).fetchmany(size=years_back)
    return list(r[Constants.ASMT_PERIOD_YEAR] for r in results)


@cache_region('public.very_shortlived')
def get_student_reg_academic_years(state_code, tenant=None):
    with EdCoreDBConnection(tenant=tenant, state_code=state_code) as connection:
        student_reg = connection.get_table(Constants.STUDENT_REG)
        query = select([distinct(student_reg.c.academic_year).label(Constants.ACADEMIC_YEAR)])\
            .where(student_reg.c.state_code == state_code).order_by(student_reg.c.academic_year.desc())
        results = connection.get_result(query)
    return list(result[Constants.ACADEMIC_YEAR] for result in results)


def get_default_asmt_academic_year(params, is_public=False):
    '''
    Get latest academic year by state code as default.
    '''
    state_code = params.get(Constants.STATECODE)
    return get_asmt_academic_years(state_code, None, None, is_public)[0]


def set_default_year_back(year_back):
    '''
    Set default year back.
    '''
    if not year_back:
        return
    global DEFAULT_YEAR_BACK
    DEFAULT_YEAR_BACK = int(year_back)
