'''
Created on Jan 13, 2013

@author: tosako
'''
from string import capwords
from sqlalchemy.sql.expression import and_
from edapi.decorators import report_config, user_info
from smarter.reports.helpers.name_formatter import format_full_name
from edapi.exceptions import NotFoundException
from edapi.logging import audit_event
from smarter.reports.helpers.breadcrumbs import get_breadcrumbs_context
from smarter.reports.helpers.assessments import get_cut_points, \
    get_overall_asmt_interval, get_claims, get_accommodations
from smarter.security.context import select_with_context,\
    get_current_request_context
from smarter.reports.helpers.constants import Constants
from smarter.reports.helpers.constants import AssessmentType
from smarter.reports.helpers.metadata import get_custom_metadata, \
    get_subjects_map
from edcore.database.edcore_connector import EdCoreDBConnection
from smarter.reports.student_administration import get_asmt_administration_years_isr
from smarter.security.tenant import validate_user_tenant
from smarter_common.security.constants import RolesConstants
import logging
from sqlalchemy.sql.functions import func


logger = logging.getLogger('smarter')


REPORT_NAME = 'individual_student_report'


def __prepare_query(connector, params):
    '''
    Returns query for individual student report
    '''
    assessment_guid = params.get(Constants.ASSESSMENTGUID)
    student_id = params.get(Constants.STUDENTGUID)
    state_code = params.get(Constants.STATECODE)
    date_taken = params.get(Constants.DATETAKEN)
    asmt_type = params.get(Constants.ASMTTYPE)
    asmt_year = params.get(Constants.ASMTYEAR)

    fact_asmt_outcome_vw = connector.get_table('fact_asmt_outcome_vw')
    dim_student = connector.get_table('dim_student')
    dim_asmt = connector.get_table('dim_asmt')
    query = select_with_context([fact_asmt_outcome_vw.c.student_id,
                                dim_student.c.first_name.label('first_name'),
                                dim_student.c.middle_name.label('middle_name'),
                                dim_student.c.last_name.label('last_name'),
                                fact_asmt_outcome_vw.c.enrl_grade.label('grade'),
                                fact_asmt_outcome_vw.c.district_id.label('district_id'),
                                fact_asmt_outcome_vw.c.school_id.label('school_id'),
                                fact_asmt_outcome_vw.c.state_code.label('state_code'),
                                fact_asmt_outcome_vw.c.date_taken.label('date_taken'),
                                dim_asmt.c.asmt_subject.label('asmt_subject'),
                                dim_asmt.c.asmt_period.label('asmt_period'),
                                dim_asmt.c.asmt_period_year.label('asmt_period_year'),
                                dim_asmt.c.asmt_type.label('asmt_type'),
                                dim_asmt.c.asmt_score_min.label('asmt_score_min'),
                                dim_asmt.c.asmt_score_max.label('asmt_score_max'),
                                dim_asmt.c.asmt_perf_lvl_name_1.label("asmt_cut_point_name_1"),
                                dim_asmt.c.asmt_perf_lvl_name_2.label("asmt_cut_point_name_2"),
                                dim_asmt.c.asmt_perf_lvl_name_3.label("asmt_cut_point_name_3"),
                                dim_asmt.c.asmt_perf_lvl_name_4.label("asmt_cut_point_name_4"),
                                dim_asmt.c.asmt_perf_lvl_name_5.label("asmt_cut_point_name_5"),
                                dim_asmt.c.asmt_cut_point_1.label("asmt_cut_point_1"),
                                dim_asmt.c.asmt_cut_point_2.label("asmt_cut_point_2"),
                                dim_asmt.c.asmt_cut_point_3.label("asmt_cut_point_3"),
                                dim_asmt.c.asmt_cut_point_4.label("asmt_cut_point_4"),
                                dim_asmt.c.asmt_claim_perf_lvl_name_1.label("asmt_claim_perf_lvl_name_1"),
                                dim_asmt.c.asmt_claim_perf_lvl_name_2.label("asmt_claim_perf_lvl_name_2"),
                                dim_asmt.c.asmt_claim_perf_lvl_name_3.label("asmt_claim_perf_lvl_name_3"),
                                fact_asmt_outcome_vw.c.asmt_grade.label('asmt_grade'),
                                fact_asmt_outcome_vw.c.asmt_score.label('asmt_score'),
                                fact_asmt_outcome_vw.c.asmt_score_range_min.label('asmt_score_range_min'),
                                fact_asmt_outcome_vw.c.asmt_score_range_max.label('asmt_score_range_max'),
                                fact_asmt_outcome_vw.c.date_taken_day.label('date_taken_day'),
                                fact_asmt_outcome_vw.c.date_taken_month.label('date_taken_month'),
                                fact_asmt_outcome_vw.c.date_taken_year.label('date_taken_year'),
                                fact_asmt_outcome_vw.c.asmt_perf_lvl.label('asmt_perf_lvl'),
                                dim_asmt.c.asmt_claim_1_name.label('asmt_claim_1_name'),
                                dim_asmt.c.asmt_claim_2_name.label('asmt_claim_2_name'),
                                dim_asmt.c.asmt_claim_3_name.label('asmt_claim_3_name'),
                                dim_asmt.c.asmt_claim_4_name.label('asmt_claim_4_name'),
                                dim_asmt.c.asmt_claim_1_score_min.label('asmt_claim_1_score_min'),
                                dim_asmt.c.asmt_claim_2_score_min.label('asmt_claim_2_score_min'),
                                dim_asmt.c.asmt_claim_3_score_min.label('asmt_claim_3_score_min'),
                                dim_asmt.c.asmt_claim_4_score_min.label('asmt_claim_4_score_min'),
                                dim_asmt.c.asmt_claim_1_score_max.label('asmt_claim_1_score_max'),
                                dim_asmt.c.asmt_claim_2_score_max.label('asmt_claim_2_score_max'),
                                dim_asmt.c.asmt_claim_3_score_max.label('asmt_claim_3_score_max'),
                                dim_asmt.c.asmt_claim_4_score_max.label('asmt_claim_4_score_max'),
                                fact_asmt_outcome_vw.c.asmt_claim_1_score.label('asmt_claim_1_score'),
                                fact_asmt_outcome_vw.c.asmt_claim_2_score.label('asmt_claim_2_score'),
                                fact_asmt_outcome_vw.c.asmt_claim_3_score.label('asmt_claim_3_score'),
                                fact_asmt_outcome_vw.c.asmt_claim_4_score.label('asmt_claim_4_score'),
                                fact_asmt_outcome_vw.c.asmt_claim_1_score_range_min.label('asmt_claim_1_score_range_min'),
                                fact_asmt_outcome_vw.c.asmt_claim_2_score_range_min.label('asmt_claim_2_score_range_min'),
                                fact_asmt_outcome_vw.c.asmt_claim_3_score_range_min.label('asmt_claim_3_score_range_min'),
                                fact_asmt_outcome_vw.c.asmt_claim_4_score_range_min.label('asmt_claim_4_score_range_min'),
                                fact_asmt_outcome_vw.c.asmt_claim_1_score_range_max.label('asmt_claim_1_score_range_max'),
                                fact_asmt_outcome_vw.c.asmt_claim_2_score_range_max.label('asmt_claim_2_score_range_max'),
                                fact_asmt_outcome_vw.c.asmt_claim_3_score_range_max.label('asmt_claim_3_score_range_max'),
                                fact_asmt_outcome_vw.c.asmt_claim_4_score_range_max.label('asmt_claim_4_score_range_max'),
                                fact_asmt_outcome_vw.c.asmt_claim_1_perf_lvl.label('asmt_claim_1_perf_lvl'),
                                fact_asmt_outcome_vw.c.asmt_claim_2_perf_lvl.label('asmt_claim_2_perf_lvl'),
                                fact_asmt_outcome_vw.c.asmt_claim_3_perf_lvl.label('asmt_claim_3_perf_lvl'),
                                fact_asmt_outcome_vw.c.asmt_claim_4_perf_lvl.label('asmt_claim_4_perf_lvl'),
                                fact_asmt_outcome_vw.c.acc_asl_video_embed.label('acc_asl_video_embed'),
                                fact_asmt_outcome_vw.c.acc_noise_buffer_nonembed.label('acc_noise_buffer_nonembed'),
                                fact_asmt_outcome_vw.c.acc_print_on_demand_items_nonembed.label('acc_print_on_demand_items_nonembed'),
                                fact_asmt_outcome_vw.c.acc_braile_embed.label('acc_braile_embed'),
                                fact_asmt_outcome_vw.c.acc_closed_captioning_embed.label('acc_closed_captioning_embed'),
                                fact_asmt_outcome_vw.c.acc_text_to_speech_embed.label('acc_text_to_speech_embed'),
                                fact_asmt_outcome_vw.c.acc_abacus_nonembed.label('acc_abacus_nonembed'),
                                fact_asmt_outcome_vw.c.acc_alternate_response_options_nonembed.label('acc_alternate_response_options_nonembed'),
                                fact_asmt_outcome_vw.c.acc_calculator_nonembed.label('acc_calculator_nonembed'),
                                fact_asmt_outcome_vw.c.acc_multiplication_table_nonembed.label('acc_multiplication_table_nonembed'),
                                fact_asmt_outcome_vw.c.acc_print_on_demand_nonembed.label('acc_print_on_demand_nonembed'),
                                fact_asmt_outcome_vw.c.acc_read_aloud_nonembed.label('acc_read_aloud_nonembed'),
                                fact_asmt_outcome_vw.c.acc_scribe_nonembed.label('acc_scribe_nonembed'),
                                fact_asmt_outcome_vw.c.acc_speech_to_text_nonembed.label('acc_speech_to_text_nonembed'),
                                fact_asmt_outcome_vw.c.acc_streamline_mode.label('acc_streamline_mode'),
                                fact_asmt_outcome_vw.c.administration_condition.label('administration_condition'),
                                func.coalesce(fact_asmt_outcome_vw.c.complete, True).label('complete')],
                                from_obj=[fact_asmt_outcome_vw
                                          .join(dim_student, and_(fact_asmt_outcome_vw.c.student_rec_id == dim_student.c.student_rec_id))
                                          .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_asmt_outcome_vw.c.asmt_rec_id))], permission=RolesConstants.PII, state_code=state_code)
    query = query.where(and_(fact_asmt_outcome_vw.c.student_id == student_id, fact_asmt_outcome_vw.c.rec_status == Constants.CURRENT))
    if assessment_guid is not None:
        query = query.where(dim_asmt.c.asmt_guid == assessment_guid)
    if date_taken is not None:
        query = query.where(fact_asmt_outcome_vw.c.date_taken == str(date_taken))
    if asmt_type is not None:
        query = query.where(dim_asmt.c.asmt_type == asmt_type)
    if asmt_year is not None:
        query = query.where(fact_asmt_outcome_vw.c.asmt_year == asmt_year)
    query = query.order_by(dim_asmt.c.asmt_subject.desc(), dim_asmt.c.asmt_period_year.desc())
    return query


def __prepare_query_iab(connector, params):
    '''
    Returns query for individual student report for IAB
    '''
    assessment_guid = params.get(Constants.ASSESSMENTGUID)
    asmt_year = params.get(Constants.ASMTYEAR)
    student_id = params.get(Constants.STUDENTGUID)
    state_code = params.get(Constants.STATECODE)

    fact_block_asmt_outcome = connector.get_table(Constants.FACT_BLOCK_ASMT_OUTCOME)
    dim_student = connector.get_table(Constants.DIM_STUDENT)
    dim_asmt = connector.get_table(Constants.DIM_ASMT)
    query = select_with_context([fact_block_asmt_outcome.c.student_id,
                                dim_student.c.first_name.label('first_name'),
                                dim_student.c.middle_name.label('middle_name'),
                                dim_student.c.last_name.label('last_name'),
                                fact_block_asmt_outcome.c.enrl_grade.label('enrl_grade'),
                                fact_block_asmt_outcome.c.district_id.label('district_id'),
                                fact_block_asmt_outcome.c.school_id.label('school_id'),
                                fact_block_asmt_outcome.c.state_code.label('state_code'),
                                dim_asmt.c.asmt_subject.label('asmt_subject'),
                                dim_asmt.c.asmt_period.label('asmt_period'),
                                dim_asmt.c.asmt_period_year.label('asmt_period_year'),
                                fact_block_asmt_outcome.c.date_taken.label('date_taken'),
                                dim_asmt.c.asmt_type.label('asmt_type'),
                                dim_asmt.c.asmt_score_min.label('asmt_score_min'),
                                dim_asmt.c.asmt_score_max.label('asmt_score_max'),
                                dim_asmt.c.asmt_perf_lvl_name_1.label("asmt_cut_point_name_1"),
                                dim_asmt.c.asmt_perf_lvl_name_2.label("asmt_cut_point_name_2"),
                                dim_asmt.c.asmt_perf_lvl_name_3.label("asmt_cut_point_name_3"),
                                dim_asmt.c.asmt_perf_lvl_name_4.label("asmt_cut_point_name_4"),
                                dim_asmt.c.asmt_perf_lvl_name_5.label("asmt_cut_point_name_5"),
                                dim_asmt.c.asmt_cut_point_1.label("asmt_cut_point_1"),
                                dim_asmt.c.asmt_cut_point_2.label("asmt_cut_point_2"),
                                dim_asmt.c.asmt_cut_point_3.label("asmt_cut_point_3"),
                                dim_asmt.c.asmt_cut_point_4.label("asmt_cut_point_4"),
                                dim_asmt.c.asmt_claim_perf_lvl_name_1.label("asmt_claim_perf_lvl_name_1"),
                                dim_asmt.c.asmt_claim_perf_lvl_name_2.label("asmt_claim_perf_lvl_name_2"),
                                dim_asmt.c.asmt_claim_perf_lvl_name_3.label("asmt_claim_perf_lvl_name_3"),
                                fact_block_asmt_outcome.c.asmt_grade.label('asmt_grade'),
                                fact_block_asmt_outcome.c.date_taken_day.label('date_taken_day'),
                                fact_block_asmt_outcome.c.date_taken_month.label('date_taken_month'),
                                fact_block_asmt_outcome.c.date_taken_year.label('date_taken_year'),
                                dim_asmt.c.asmt_claim_1_name.label('asmt_claim_1_name'),
                                dim_asmt.c.asmt_claim_2_name.label('asmt_claim_2_name'),
                                dim_asmt.c.asmt_claim_3_name.label('asmt_claim_3_name'),
                                dim_asmt.c.asmt_claim_4_name.label('asmt_claim_4_name'),
                                dim_asmt.c.asmt_claim_1_score_min.label('asmt_claim_1_score_min'),
                                dim_asmt.c.asmt_claim_2_score_min.label('asmt_claim_2_score_min'),
                                dim_asmt.c.asmt_claim_3_score_min.label('asmt_claim_3_score_min'),
                                dim_asmt.c.asmt_claim_4_score_min.label('asmt_claim_4_score_min'),
                                dim_asmt.c.asmt_claim_1_score_max.label('asmt_claim_1_score_max'),
                                dim_asmt.c.asmt_claim_2_score_max.label('asmt_claim_2_score_max'),
                                dim_asmt.c.asmt_claim_3_score_max.label('asmt_claim_3_score_max'),
                                dim_asmt.c.asmt_claim_4_score_max.label('asmt_claim_4_score_max'),
                                fact_block_asmt_outcome.c.asmt_claim_1_score.label('asmt_claim_1_score'),
                                fact_block_asmt_outcome.c.asmt_claim_1_score_range_min.label('asmt_claim_1_score_range_min'),
                                fact_block_asmt_outcome.c.asmt_claim_1_score_range_max.label('asmt_claim_1_score_range_max'),
                                fact_block_asmt_outcome.c.asmt_claim_1_perf_lvl.label('asmt_claim_1_perf_lvl'),
                                fact_block_asmt_outcome.c.administration_condition.label('administration_condition'),
                                func.coalesce(fact_block_asmt_outcome.c.complete, True).label('complete')],
                                from_obj=[fact_block_asmt_outcome
                                          .join(dim_student, and_(fact_block_asmt_outcome.c.student_rec_id == dim_student.c.student_rec_id))
                                          .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_block_asmt_outcome.c.asmt_rec_id))], permission=RolesConstants.PII, state_code=state_code)
    query = query.where(and_(fact_block_asmt_outcome.c.student_id == student_id, fact_block_asmt_outcome.c.rec_status == Constants.CURRENT, dim_asmt.c.asmt_type == AssessmentType.INTERIM_ASSESSMENT_BLOCKS))
    if assessment_guid is not None:
        query = query.where(dim_asmt.c.asmt_guid == assessment_guid)
    if asmt_year is not None:
        query = query.where(fact_block_asmt_outcome.c.asmt_year == asmt_year)
    query = query.order_by(dim_asmt.c.asmt_subject.desc(), fact_block_asmt_outcome.c.asmt_grade.desc(), fact_block_asmt_outcome.c.date_taken.desc())
    return query


def __calculateClaimScoreRelativeDifference(item):
    '''
    calcluate relative difference for each claims
    1. find absluate max claim score
    2. calculate relative difference
    '''
    newItem = item.copy()
    asmt_score = newItem['asmt_score']
    claims = newItem['claims']
    maxAbsDiffScore = 0
    for claim in claims:
        score = int(claim['score'])
        # keep track max score difference
        if maxAbsDiffScore < abs(asmt_score - score):
            maxAbsDiffScore = abs(asmt_score - score)
    for claim in claims:
        score = int(claim['score'])
        if maxAbsDiffScore == 0:
            claim['claim_score_relative_difference'] = 0
        else:
            claim['claim_score_relative_difference'] = int((score - asmt_score) / maxAbsDiffScore * 100)
    return newItem


def __arrange_results(results, subjects_map, custom_metadata_map):
    '''
    This method arranges the data retrieved from the db to make it easier to consume by the client
    '''
    new_results = []
    for result in results:

        result['student_full_name'] = format_full_name(result['first_name'], result['middle_name'], result['last_name'])
        # asmt_type is an enum, so we would to capitalize it to make it presentable
        result['asmt_type'] = capwords(result['asmt_type'], ' ')
        result['asmt_score_interval'] = get_overall_asmt_interval(result)

        # custom metadata
        subject_name = subjects_map[result["asmt_subject"]]
        custom = custom_metadata_map.get(subject_name)
        # format and rearrange cutpoints
        result = get_cut_points(custom, result)

        result['claims'] = get_claims(number_of_claims=5, result=result, include_names=True, include_scores=True, include_min_max_scores=True, include_indexer=True)
        result['accommodations'] = get_accommodations(result=result)

        new_results.append(result)

    # rearranging the json so we could use it more easily with mustache
    for idx, value in enumerate(new_results):
        new_results[idx] = __calculateClaimScoreRelativeDifference(value)
    return {"all_results": new_results}


def __arrange_results_iab(results, subjects_map, custom_metadata_map):
    '''
    This method arranges the data retrieved from the db to make it easier to consume by the client
    '''
    iab_results = {}
    if len(results) is 0:
        return iab_results
    first_result = results[0]
    iab_results['student_full_name'] = format_full_name(first_result['first_name'], first_result['middle_name'], first_result['last_name'])
    iab_results['first_name'] = first_result.get('first_name')
    iab_results['middle_name'] = first_result.get('middle_name')
    iab_results['last_name'] = first_result.get('last_name')
    iab_results['asmt_grade'] = first_result.get('asmt_grade')
    iab_results['asmt_type'] = capwords(first_result.get('asmt_type'), ' ')
    iab_results['asmt_period_year'] = first_result.get('asmt_period_year')
    iab_results['student_id'] = first_result.get('student_id')

    # Go through each of the different subjects ELA, Math etc.
    subject_data = {}
    for alias in subjects_map.values():
        subject_data[alias] = []
    # Check each DB result against the subject
    for result in results:
        subject_list = {}
        subject = result['asmt_subject']
        subject_list['claims'] = get_claims(number_of_claims=1, result=result, include_names=True, include_scores=False, include_min_max_scores=False, include_indexer=False)
        subject_list['grade'] = result.get('asmt_grade')
        subject_list['date_taken'] = result.get('date_taken')
        subject_data[subjects_map.get(subject)].append(subject_list)
    # Create map from subject to all value for it's type
    for k, v in subject_data.items():
        iab_results[k] = v
    return {"all_results": iab_results}


@report_config(name=REPORT_NAME,
               params={
                   Constants.STATECODE: {
                       "type": "string",
                       "required": True,
                       "pattern": "^[a-zA-Z]{2}$"},
                   Constants.STUDENTGUID: {
                       "type": "string",
                       "required": True,
                       "pattern": "^[a-zA-Z0-9\-]{0,50}$"},
                   Constants.ASSESSMENTGUID: {
                       "type": "string",
                       "required": False,
                       "pattern": "^[a-zA-Z0-9\-]{0,50}$"},
                   Constants.ASMTYEAR: {
                       "type": "integer",
                       "required": True,
                       "pattern": "^[1-9][0-9]{3}$"},
                   Constants.DATETAKEN: {
                       "type": "integer",
                       "required": False,
                       "pattern": "^[1-9]{8}$"},
                   Constants.ASMTTYPE: {
                       "type": "string",
                       "required": True,
                       "pattern": "^(" + AssessmentType.INTERIM_ASSESSMENT_BLOCKS + "|" + AssessmentType.SUMMATIVE + "|" + AssessmentType.INTERIM_COMPREHENSIVE + ")$"}
               })
@validate_user_tenant
@user_info
@get_current_request_context
@audit_event()
def get_student_report(params):
    '''
    Individual Student Report
    '''
    student_id = params[Constants.STUDENTGUID]
    state_code = params[Constants.STATECODE]
    academic_year = params.get(Constants.ASMTYEAR)
    asmt_type = params.get(Constants.ASMTTYPE)
    asmt_type = asmt_type if asmt_type and asmt_type == AssessmentType.INTERIM_ASSESSMENT_BLOCKS else None

    with EdCoreDBConnection(state_code=state_code) as connection:
        # choose query IAB or other assessment
        query_function = {AssessmentType.INTERIM_ASSESSMENT_BLOCKS: __prepare_query_iab, None: __prepare_query}
        # choose arrange results for the client IAB or other assessment
        arrange_function = {AssessmentType.INTERIM_ASSESSMENT_BLOCKS: __arrange_results_iab, None: __arrange_results}
        query = query_function[asmt_type](connection, params)
        result = connection.get_result(query)
        if not result:
            logger.error("Individual student report: there are no results for student id : %s", student_id)
            raise NotFoundException("There are no results for student id {0}".format(student_id))
        records = [record for record in result if record['asmt_period_year'] == academic_year]
        first_student = records[0] if len(records) > 0 else result[0]
        state_code = first_student[Constants.STATE_CODE]
        district_id = first_student[Constants.DISTRICT_ID]
        school_id = first_student[Constants.SCHOOL_ID]
        asmt_grade = first_student['asmt_grade']
        student_name = format_full_name(first_student['first_name'], first_student['middle_name'], first_student['last_name'])
        context = get_breadcrumbs_context(state_code=state_code, district_id=district_id, school_id=school_id, asmt_grade=asmt_grade, student_name=student_name)
        student_report_asmt_administration = get_asmt_administration_years_isr(state_code, student_ids=student_id)

        # color metadata
        custom_metadata_map = get_custom_metadata(result[0].get(Constants.STATE_CODE), None)
        # subjects map
        subjects_map = get_subjects_map()
        result = arrange_function[asmt_type](result, subjects_map, custom_metadata_map)

        result['context'] = context
        result[Constants.METADATA] = {Constants.BRANDING: custom_metadata_map.get(Constants.BRANDING)}
        result[Constants.SUBJECTS] = {v: k for k, v in subjects_map.items()}
        result['asmt_administration'] = student_report_asmt_administration
    return result
