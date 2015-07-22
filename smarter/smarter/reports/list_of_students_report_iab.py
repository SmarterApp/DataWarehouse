'''
Created on Oct 20, 2014

@author: tosako
'''
from edcore.database.edcore_connector import EdCoreDBConnection
from smarter.reports.helpers.constants import Constants, AssessmentType
from smarter.security.context import select_with_context
from sqlalchemy.sql.expression import and_
from smarter_common.security.constants import RolesConstants
from smarter.reports.helpers.filters import apply_filter_to_query, \
    get_student_demographic
from smarter.reports.helpers.metadata import get_subjects_map
from smarter.reports.list_of_students_report_utils import get_group_filters, \
    __reverse_map
from smarter.reports.helpers.breadcrumbs import get_breadcrumbs_context
from smarter.reports.student_administration import get_asmt_administration_years, \
    get_asmt_academic_years
from smarter.reports.helpers.compare_pop_stat_report import get_not_stated_count
from smarter.reports.helpers.assessments import get_claims
import collections


def get_list_of_students_report_iab(params):
    stateCode = str(params[Constants.STATECODE])
    districtId = str(params[Constants.DISTRICTGUID])
    schoolId = str(params[Constants.SCHOOLGUID])
    asmtGrade = params.get(Constants.ASMTGRADE)
    asmtSubject = params.get(Constants.ASMTSUBJECT)
    asmtYear = params.get(Constants.ASMTYEAR)
    results = get_list_of_students_iab(params)
    subjects_map = get_subjects_map(asmtSubject)
    los_results = {}
    los_results[Constants.ASSESSMENTS] = format_assessments_iab(results, subjects_map)
    los_results['groups'] = get_group_filters(results)

    # color metadata
    los_results[Constants.CONTEXT] = get_breadcrumbs_context(state_code=stateCode, district_id=districtId, school_id=schoolId, asmt_grade=asmtGrade)
    los_results[Constants.SUBJECTS] = __reverse_map(subjects_map)

    # Additional queries for LOS report
    los_results[Constants.ASMT_ADMINISTRATION] = get_asmt_administration_years(stateCode, districtId, schoolId, asmtGrade, asmt_year=asmtYear)
    los_results[Constants.NOT_STATED] = get_not_stated_count(params)
    los_results[Constants.ASMT_PERIOD_YEAR] = get_asmt_academic_years(stateCode)
    los_results[Constants.INTERIM_ASSESSMENT_BLOCKS] = get_IAB_claims(los_results[Constants.ASSESSMENTS][AssessmentType.INTERIM_ASSESSMENT_BLOCKS], los_results[Constants.SUBJECTS])

    return los_results


def get_list_of_students_iab(params):
    stateCode = str(params[Constants.STATECODE])
    districtId = str(params[Constants.DISTRICTGUID])
    schoolId = str(params[Constants.SCHOOLGUID])
    asmtGrade = params.get(Constants.ASMTGRADE)
    asmtSubject = params.get(Constants.ASMTSUBJECT)
    asmtYear = params.get(Constants.ASMTYEAR)
    with EdCoreDBConnection(state_code=stateCode) as connector:
        dim_student = connector.get_table(Constants.DIM_STUDENT)
        dim_asmt = connector.get_table(Constants.DIM_ASMT)
        fact_block_asmt_outcome = connector.get_table(Constants.FACT_BLOCK_ASMT_OUTCOME)
        query = select_with_context([dim_student.c.student_id.label('student_id'),
                                     dim_student.c.first_name.label('first_name'),
                                     dim_student.c.middle_name.label('middle_name'),
                                     dim_student.c.last_name.label('last_name'),
                                     fact_block_asmt_outcome.c.state_code.label('state_code'),
                                     fact_block_asmt_outcome.c.enrl_grade.label('enrollment_grade'),
                                     fact_block_asmt_outcome.c.asmt_grade.label('asmt_grade'),
                                     dim_asmt.c.asmt_subject.label('asmt_subject'),
                                     dim_asmt.c.effective_date.label('effective_date'),
                                     fact_block_asmt_outcome.c.date_taken.label('date_taken'),
                                     dim_asmt.c.asmt_type.label('asmt_type'),
                                     dim_asmt.c.asmt_score_min.label('asmt_score_min'),
                                     dim_asmt.c.asmt_score_max.label('asmt_score_max'),
                                     dim_asmt.c.asmt_claim_1_name.label('asmt_claim_1_name'),
                                     fact_block_asmt_outcome.c.asmt_claim_1_score.label('asmt_claim_1_score'),
                                     fact_block_asmt_outcome.c.asmt_claim_1_score_range_min.label('asmt_claim_1_score_range_min'),
                                     fact_block_asmt_outcome.c.asmt_claim_1_score_range_max.label('asmt_claim_1_score_range_max'),
                                     # demographic information
                                     fact_block_asmt_outcome.c.dmg_eth_derived.label('dmg_eth_derived'),
                                     fact_block_asmt_outcome.c.dmg_prg_iep.label('dmg_prg_iep'),
                                     fact_block_asmt_outcome.c.dmg_prg_lep.label('dmg_prg_lep'),
                                     fact_block_asmt_outcome.c.dmg_prg_504.label('dmg_prg_504'),
                                     fact_block_asmt_outcome.c.dmg_sts_ecd.label('dmg_sts_ecd'),
                                     fact_block_asmt_outcome.c.dmg_sts_mig.label('dmg_sts_mig'),
                                     fact_block_asmt_outcome.c.sex.label('sex'),
                                     # grouping information
                                     dim_student.c.group_1_id.label('group_1_id'),
                                     dim_student.c.group_1_text.label('group_1_text'),
                                     dim_student.c.group_2_id.label('group_2_id'),
                                     dim_student.c.group_2_text.label('group_2_text'),
                                     dim_student.c.group_3_id.label('group_3_id'),
                                     dim_student.c.group_3_text.label('group_3_text'),
                                     dim_student.c.group_4_id.label('group_4_id'),
                                     dim_student.c.group_4_text.label('group_4_text'),
                                     dim_student.c.group_5_id.label('group_5_id'),
                                     dim_student.c.group_5_text.label('group_5_text'),
                                     dim_student.c.group_6_id.label('group_6_id'),
                                     dim_student.c.group_6_text.label('group_6_text'),
                                     dim_student.c.group_7_id.label('group_7_id'),
                                     dim_student.c.group_7_text.label('group_7_text'),
                                     dim_student.c.group_8_id.label('group_8_id'),
                                     dim_student.c.group_8_text.label('group_8_text'),
                                     dim_student.c.group_9_id.label('group_9_id'),
                                     dim_student.c.group_9_text.label('group_9_text'),
                                     dim_student.c.group_10_id.label('group_10_id'),
                                     dim_student.c.group_10_text.label('group_10_text'),
                                     dim_asmt.c.asmt_claim_perf_lvl_name_1.label('asmt_claim_perf_lvl_name_1'),
                                     dim_asmt.c.asmt_claim_perf_lvl_name_2.label('asmt_claim_perf_lvl_name_2'),
                                     dim_asmt.c.asmt_claim_perf_lvl_name_3.label('asmt_claim_perf_lvl_name_3'),
                                     fact_block_asmt_outcome.c.asmt_claim_1_perf_lvl.label('asmt_claim_1_perf_lvl')],
                                    from_obj=[fact_block_asmt_outcome
                                              .join(dim_student, and_(fact_block_asmt_outcome.c.student_rec_id == dim_student.c.student_rec_id))
                                              .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_block_asmt_outcome.c.asmt_rec_id))], permission=RolesConstants.PII, state_code=stateCode)
        query = query.where(fact_block_asmt_outcome.c.state_code == stateCode)
        query = query.where(and_(fact_block_asmt_outcome.c.school_id == schoolId))
        query = query.where(and_(fact_block_asmt_outcome.c.district_id == districtId))
        query = query.where(and_(fact_block_asmt_outcome.c.asmt_year == asmtYear))
        query = query.where(and_(fact_block_asmt_outcome.c.rec_status == Constants.CURRENT))
        query = query.where(and_(fact_block_asmt_outcome.c.asmt_type == AssessmentType.INTERIM_ASSESSMENT_BLOCKS))
        query = apply_filter_to_query(query, fact_block_asmt_outcome, dim_student, params)
        if asmtSubject is not None:
            query = query.where(and_(dim_asmt.c.asmt_subject.in_(asmtSubject)))
        if asmtGrade is not None:
            query = query.where(and_(fact_block_asmt_outcome.c.asmt_grade == asmtGrade))

        query = query.order_by(dim_student.c.last_name).order_by(dim_student.c.first_name).order_by(fact_block_asmt_outcome.c.date_taken.desc())
        return connector.get_result(query)


def get_IAB_claims(results, subjects):
    claim_names = {}
    for studentId in results.keys():
        for subject_name in subjects.keys():
            claim_list = results[studentId].get(subject_name)
            if not claim_list:
                continue
            for claim, assessments in claim_list.items():
                claim_name = claim_names.get(subject_name, dict())
                temp = claim_name.get(claim, set())
                for asmt in assessments:
                    temp.add(asmt["date_taken"])
                claim_name[claim] = temp
                claim_names[subject_name] = claim_name
    for subject_name, claims in claim_names.items():
        for claim_name, dates_taken_on in claims.items():
            claim_names[subject_name][claim_name] = sorted(list(dates_taken_on), reverse=True)
    return claim_names


def format_assessments_iab(results, subjects_map):
    '''
    Format student assessments.
    '''

    assessments = {}
    # Formatting data for Front End
    for result in results:
        date_taken = result['date_taken']  # e.g. 20140401
        studentId = result['student_id']  # e.g. student_1
        student = assessments.get(studentId, {})
        if not student:
            student['student_id'] = studentId
            student['student_first_name'] = result['first_name']
            student['student_middle_name'] = result['middle_name']
            student['student_last_name'] = result['last_name']
            student['enrollment_grade'] = result['enrollment_grade']
            student['state_code'] = result['state_code']
            student['demographic'] = get_student_demographic(result)
            student[Constants.ROWID] = result['student_id']
            student['group'] = set()  # for student group filter

        for i in range(1, 11):
            if result['group_{count}_id'.format(count=i)] is not None:
                student['group'].add(result['group_{count}_id'.format(count=i)])

        assessment = {Constants.DATE_TAKEN: date_taken}
        assessment['asmt_grade'] = result['asmt_grade']
        claims = assessment.get('claims', [])
        claim = get_claims(number_of_claims=1, result=result, include_scores=False, include_names=True)[0]
        claims.append(claim)
        assessment['claims'] = claims
        claim_name = claims[0]['name']

        subject = subjects_map[result['asmt_subject']]
        claim_dict = student.get(subject, {})
        date_taken_data = claim_dict.get(claim_name, [])

        date_taken_data.append(assessment)
        claim_dict[claim_name] = date_taken_data
        student[subject] = claim_dict
        assessments[studentId] = student

    for student in assessments.values():
        student['group'] = list(student['group'])

    return {AssessmentType.INTERIM_ASSESSMENT_BLOCKS: assessments}
