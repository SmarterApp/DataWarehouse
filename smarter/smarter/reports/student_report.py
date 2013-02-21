'''
Created on Jan 13, 2013

@author: tosako
'''


from edapi.utils import report_config
from sqlalchemy.sql import select
from database.connector import DBConnector
import json


def __prepare_query(connector, student_id, assessment_id):
    # get table metadatas
    fact_asmt_outcome = connector.get_table('fact_asmt_outcome')
    dim_student = connector.get_table('dim_student')
    dim_asmt = connector.get_table('dim_asmt')
    dim_staff = connector.get_table('dim_staff')
    query = select([fact_asmt_outcome.c.student_id,
                    dim_student.c.first_name.label('student_first_name'),
                    dim_student.c.middle_name.label('student_middle_name'),
                    dim_student.c.last_name.label('student_last_name'),
                    dim_asmt.c.asmt_subject.label('asmt_subject'),
                    dim_asmt.c.asmt_period.label('asmt_period'),
                    dim_asmt.c.asmt_type.label('asmt_type'),
                    dim_asmt.c.asmt_perf_lvl_name_1.label("asmt_cut_point_name_1"),
                    dim_asmt.c.asmt_perf_lvl_name_2.label("asmt_cut_point_name_2"),
                    dim_asmt.c.asmt_perf_lvl_name_3.label("asmt_cut_point_name_3"),
                    dim_asmt.c.asmt_perf_lvl_name_4.label("asmt_cut_point_name_4"),
                    dim_asmt.c.asmt_perf_lvl_name_5.label("asmt_cut_point_name_5"),
                    dim_asmt.c.asmt_cut_point_1.label("asmt_cut_point_1"),
                    dim_asmt.c.asmt_cut_point_2.label("asmt_cut_point_2"),
                    dim_asmt.c.asmt_cut_point_3.label("asmt_cut_point_3"),
                    dim_asmt.c.asmt_cut_point_4.label("asmt_cut_point_4"),
                    dim_asmt.c.asmt_claim_1_score_min.label('asmt_claim_1_score_min'),
                    dim_asmt.c.asmt_claim_2_score_min.label('asmt_claim_2_score_min'),
                    dim_asmt.c.asmt_claim_3_score_min.label('asmt_claim_3_score_min'),
                    dim_asmt.c.asmt_claim_4_score_min.label('asmt_claim_4_score_min'),
                    dim_asmt.c.asmt_claim_1_score_max.label('asmt_claim_1_score_max'),
                    dim_asmt.c.asmt_claim_2_score_max.label('asmt_claim_2_score_max'),
                    dim_asmt.c.asmt_claim_3_score_max.label('asmt_claim_3_score_max'),
                    dim_asmt.c.asmt_claim_4_score_max.label('asmt_claim_4_score_max'),
                    dim_asmt.c.asmt_custom_metadata.label('asmt_custom_metadata'),
                    fact_asmt_outcome.c.asmt_grade.label('asmt_grade'),
                    fact_asmt_outcome.c.asmt_score.label('asmt_score'),
                    fact_asmt_outcome.c.date_taken_day.label('date_taken_day'),
                    fact_asmt_outcome.c.date_taken_month.label('date_taken_month'),
                    fact_asmt_outcome.c.date_taken_year.label('date_taken_year'),
                    dim_asmt.c.asmt_claim_1_name.label('asmt_claim_1_name'),
                    dim_asmt.c.asmt_claim_2_name.label('asmt_claim_2_name'),
                    dim_asmt.c.asmt_claim_3_name.label('asmt_claim_3_name'),
                    dim_asmt.c.asmt_claim_4_name.label('asmt_claim_4_name'),
                    fact_asmt_outcome.c.asmt_claim_1_score.label('asmt_claim_1_score'),
                    fact_asmt_outcome.c.asmt_claim_2_score.label('asmt_claim_2_score'),
                    fact_asmt_outcome.c.asmt_claim_3_score.label('asmt_claim_3_score'),
                    fact_asmt_outcome.c.asmt_claim_4_score.label('asmt_claim_4_score'),
                    dim_staff.c.first_name.label('teacher_first_name'),
                    dim_staff.c.middle_name.label('teacher_middle_name'),
                    dim_staff.c.last_name.label('teacher_last_name')],
                   from_obj=[fact_asmt_outcome.join(dim_student, fact_asmt_outcome.c.student_id == dim_student.c.student_id).join(dim_staff, fact_asmt_outcome.c.teacher_id == dim_staff.c.staff_id).join(dim_asmt, dim_asmt.c.asmt_id == fact_asmt_outcome.c.asmt_id)])
    query = query.where(fact_asmt_outcome.c.student_id == student_id)
    if assessment_id is not None:
        query = query.where(fact_asmt_outcome.c.asmt_id == assessment_id)
    return query


def arrage_results(results):
    for result in results:
        custom = json.loads(result['asmt_custom_metadata'])
        result['cut_points'] = []

        for i in range(1, 5):
            if result['asmt_cut_point_{0}'.format(i)] > 0:
                result['cut_points'].append(dict(list({
                                'name': result['asmt_claim_{0}_name'.format(i)],
                                'cut_point': result['asmt_cut_point_{0}'.format(i)],
                                }.items()) + list(custom[i - 1].items())))


@report_config(name='individual_student_report',
               params={
                   "studentId": {
                   "type": "string",
                   "required": True
                   },
                   "assessmentId": {
                   "name": "student_assessments_report",
                   "type": "string",
                   "required": False
                   }
               }
               )
def get_student_report(params, connector=None):
    '''
    report for student and student_assessment
    '''

    # if connector is not supplied, use DBConnector
    if connector is None:
        connector = DBConnector()

    # get studentId
    student_id = str(params['studentId'])

    # if assessmentId is available, read the value.
    assessment_id = None
    if 'assessmentId' in params:
        assessment_id = str(params['assessmentId'])

    # get sql session
    connector.open_connection()

    query = __prepare_query(connector, student_id, assessment_id)

    result = connector.get_result(query)

    arrage_results(result)

    # rearranging the json so we could use it more easily with mustache
    result = {"items": result}

    connector.close_connection()

    return result


@report_config(name='student_assessments_report',
               params={
                   "studentId": {
                   "type": "string",
                   "required": True
                   }
               }
               )
def get_student_assessment(params, connector=None):

    # if connector is not supplied, use DBConnector
    if connector is None:
        connector = DBConnector()

    # get studentId
    student_id = params['studentId']

    # get sql session
    connector.open_connection()

    # get table metadatas
    dim_asmt = connector.get_table('dim_asmt')
    fact_asmt_outcome = connector.get_table('fact_asmt_outcome')

    query = select([dim_asmt.c.asmt_id,
                    dim_asmt.c.asmt_subject,
                    dim_asmt.c.asmt_type,
                    dim_asmt.c.asmt_period,
                    dim_asmt.c.asmt_version,
                    dim_asmt.c.asmt_grade],
                   from_obj=[dim_asmt
                             .join(fact_asmt_outcome)])
    query = query.where(fact_asmt_outcome.c.student_id == student_id)
    query = query.order_by(dim_asmt.c.asmt_subject)
    result = connector.get_result(query)
    connector.close_connection()
    return result
