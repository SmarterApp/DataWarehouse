'''
Created on Jan 13, 2013

@author: tosako
'''
from edapi.decorators import report_config, user_info
from smarter.reports.helpers.name_formatter import format_full_name
from sqlalchemy.sql.expression import and_
from edapi.exceptions import NotFoundException
from string import capwords
from edapi.logging import audit_event
from smarter.reports.helpers.breadcrumbs import get_breadcrumbs_context
from smarter.reports.helpers.assessments import get_cut_points, \
    get_overall_asmt_interval, get_claims
from smarter.security.context import select_with_context
from smarter.reports.helpers.constants import Constants
from smarter.reports.helpers.metadata import get_custom_metadata,\
    get_subjects_map
from edcore.database.edcore_connector import EdCoreDBConnection

REPORT_NAME = 'individual_student_report'


def __prepare_query(connector, student_guid, assessment_guid):
    '''
    Returns query for individual student report
    '''
    fact_asmt_outcome = connector.get_table('fact_asmt_outcome')
    dim_student = connector.get_table('dim_student')
    dim_asmt = connector.get_table('dim_asmt')
    dim_staff = connector.get_table('dim_staff')
    query = select_with_context([fact_asmt_outcome.c.student_guid,
                                dim_student.c.first_name.label('student_first_name'),
                                dim_student.c.middle_name.label('student_middle_name'),
                                dim_student.c.last_name.label('student_last_name'),
                                dim_student.c.grade.label('grade'),
                                dim_student.c.district_guid.label('district_guid'),
                                dim_student.c.school_guid.label('school_guid'),
                                dim_student.c.state_code.label('state_code'),
                                dim_asmt.c.asmt_subject.label('asmt_subject'),
                                dim_asmt.c.asmt_period.label('asmt_period'),
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
                                fact_asmt_outcome.c.asmt_grade.label('asmt_grade'),
                                fact_asmt_outcome.c.asmt_score.label('asmt_score'),
                                fact_asmt_outcome.c.asmt_score_range_min.label('asmt_score_range_min'),
                                fact_asmt_outcome.c.asmt_score_range_max.label('asmt_score_range_max'),
                                fact_asmt_outcome.c.date_taken_day.label('date_taken_day'),
                                fact_asmt_outcome.c.date_taken_month.label('date_taken_month'),
                                fact_asmt_outcome.c.date_taken_year.label('date_taken_year'),
                                fact_asmt_outcome.c.asmt_perf_lvl.label('asmt_perf_lvl'),
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
                                fact_asmt_outcome.c.asmt_claim_1_score.label('asmt_claim_1_score'),
                                fact_asmt_outcome.c.asmt_claim_2_score.label('asmt_claim_2_score'),
                                fact_asmt_outcome.c.asmt_claim_3_score.label('asmt_claim_3_score'),
                                fact_asmt_outcome.c.asmt_claim_4_score.label('asmt_claim_4_score'),
                                fact_asmt_outcome.c.asmt_claim_1_score_range_min.label('asmt_claim_1_score_range_min'),
                                fact_asmt_outcome.c.asmt_claim_2_score_range_min.label('asmt_claim_2_score_range_min'),
                                fact_asmt_outcome.c.asmt_claim_3_score_range_min.label('asmt_claim_3_score_range_min'),
                                fact_asmt_outcome.c.asmt_claim_4_score_range_min.label('asmt_claim_4_score_range_min'),
                                fact_asmt_outcome.c.asmt_claim_1_score_range_max.label('asmt_claim_1_score_range_max'),
                                fact_asmt_outcome.c.asmt_claim_2_score_range_max.label('asmt_claim_2_score_range_max'),
                                fact_asmt_outcome.c.asmt_claim_3_score_range_max.label('asmt_claim_3_score_range_max'),
                                fact_asmt_outcome.c.asmt_claim_4_score_range_max.label('asmt_claim_4_score_range_max')],
                                from_obj=[fact_asmt_outcome
                                          .join(dim_student, and_(fact_asmt_outcome.c.student_guid == dim_student.c.student_guid,
                                                                  fact_asmt_outcome.c.section_guid == dim_student.c.section_guid))
                                          .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_asmt_outcome.c.asmt_rec_id,
                                                               dim_asmt.c.most_recent))])
    query = query.where(and_(fact_asmt_outcome.c.most_recent, fact_asmt_outcome.c.status == 'C', fact_asmt_outcome.c.student_guid == student_guid))
    if assessment_guid is not None:
        query = query.where(dim_asmt.c.asmt_guid == assessment_guid)
    query = query.order_by(dim_asmt.c.asmt_subject.desc())
    return query


def __calculateClaimScoreRelativeDifference(items):
    '''
    calcluate relative difference for each claims
    1. find absluate max claim score
    2. calculate relative difference
    '''
    newItems = items.copy()
    for item in newItems:
        asmt_score = item['asmt_score']
        claims = item['claims']
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
    return newItems


def __arrange_results(results, subjects_map, custom_metadata_map):
    '''
    This method arranges the data retreievd from the db to make it easier to consume by the client
    '''
    new_results = {}
    for result in results:

        result['student_full_name'] = format_full_name(result['student_first_name'], result['student_middle_name'], result['student_last_name'])

        # asmt_type is an enum, so we would to capitalize it to make it presentable
        result['asmt_type'] = capwords(result['asmt_type'], ' ')

        result['asmt_score_interval'] = get_overall_asmt_interval(result)

        # custom metadata
        subject_name = subjects_map[result["asmt_subject"]]
        custom = custom_metadata_map.get(subject_name)
        # format and rearrange cutpoints
        result = get_cut_points(custom, result)

        result['claims'] = get_claims(number_of_claims=5, result=result, include_names=True, include_scores=True, include_min_max_scores=True, include_indexer=True)

        if new_results.get(result['asmt_type']) is None:
            new_results[result['asmt_type']] = []

        new_results[result['asmt_type']].append(result)

    # rearranging the json so we could use it more easily with mustache
    for key, value in new_results.items():
        new_results[key] = __calculateClaimScoreRelativeDifference(value)
    return {"items": new_results}


@report_config(name=REPORT_NAME,
               params={
                   "studentGuid": {
                       "type": "string",
                       "required": True,
                       "pattern": "^[a-zA-Z0-9\-]{0,50}$"},
                   "assessmentGuid": {
                       "type": "string",
                       "required": False,
                       "pattern": "^[a-zA-Z0-9\-]{0,50}$",
                   },
               })
@audit_event()
@user_info
def get_student_report(params):
    '''
    Individual Student Report
    '''
    # get studentId
    student_guid = str(params['studentGuid'])

    # if assessmentId is available, read the value.
    assessment_guid = None
    if 'assessmentGuid' in params:
        assessment_guid = str(params['assessmentGuid'])

    with EdCoreDBConnection() as connection:
        query = __prepare_query(connection, student_guid, assessment_guid)

        result = connection.get_result(query)
        if result:
            first_student = result[0]
            student_name = format_full_name(first_student['student_first_name'], first_student['student_middle_name'], first_student['student_last_name'])
            context = get_breadcrumbs_context(district_guid=first_student['district_guid'], school_guid=first_student['school_guid'], asmt_grade=first_student['grade'], student_name=student_name)
        else:
            raise NotFoundException("There are no results for student id {0}".format(student_guid))

        # color metadata
        custom_metadata_map = get_custom_metadata(result[0].get(Constants.STATE_CODE), None)
        # subjects map
        subjects_map = get_subjects_map()
        # prepare the result for the client
        result = __arrange_results(result, subjects_map, custom_metadata_map)

        result['context'] = context
    return result
