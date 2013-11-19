'''
Created on Nov 1, 2013

@author: ejen
'''
from edcore.database.edcore_connector import EdCoreDBConnection
from sqlalchemy.sql.expression import and_
from smarter.reports.helpers.constants import Constants
from smarter.security.context import select_with_context
from psycopg2.extensions import adapt as sqlescape
from smarter.extract.format import get_column_mapping


def compile_query_to_sql_text(query):
    '''
    This function compile sql object by binding expression's free variable with its params
    :param sqlalchemy query object
    '''
    unbound_sql_code = str(query)
    params = query.compile().params
    for k, v in params.items():
        unbound_sql_code = unbound_sql_code.replace(':' + k, str(sqlescape(v)))
    return unbound_sql_code


def get_extract_assessment_query(params, limit=None, compiled=False):
    """
    private method to generate SQLAlchemy object or sql code for extraction

    :param params: for query parameters asmt_type, asmt_subject, asmt_year, limit, most_recent
    :param limit: for set up limit of result
    :param compile: True to return SQL code, otherwise just SQLALchemy object
    """
    state_code = params.get(Constants.STATECODE)
    district_guid = params.get(Constants.DISTRICTGUID)
    school_guid = params.get(Constants.SCHOOLGUID)
    asmt_grade = params.get(Constants.ASMTGRADE)
    asmt_type = params.get(Constants.ASMTTYPE)
    asmt_year = params.get(Constants.ASMTYEAR)
    asmt_subject = params.get(Constants.ASMTSUBJECT)

    dim_student_label = get_column_mapping(Constants.DIM_STUDENT)
    dim_inst_hier_label = get_column_mapping(Constants.DIM_INST_HIER)
    dim_asmt_label = get_column_mapping(Constants.DIM_ASMT)
    fact_asmt_outcome_label = get_column_mapping(Constants.FACT_ASMT_OUTCOME)

    with EdCoreDBConnection() as connector:
        dim_student = connector.get_table(Constants.DIM_STUDENT)
        dim_asmt = connector.get_table(Constants.DIM_ASMT)
        dim_inst_hier = connector.get_table(Constants.DIM_INST_HIER)
        fact_asmt_outcome = connector.get_table(Constants.FACT_ASMT_OUTCOME)
        # TODO:  Defect, asmt_guid is not mapping correctly from ref_table_data
        # guid_asmt_location is currently missing
        query = select_with_context([dim_asmt.c.asmt_guid.label(dim_asmt_label.get('asmt_guid', 'guid_asmt')),
                                    fact_asmt_outcome.c.where_taken_name.label(dim_asmt_label.get('where_taken_name', 'name_asmt_location')),
                                    fact_asmt_outcome.c.asmt_grade.label(fact_asmt_outcome_label.get('asmt_grade', 'asmt_grade')),
                                    dim_inst_hier.c.state_name.label(dim_inst_hier_label.get('state_name', 'name_state')),
                                    dim_inst_hier.c.state_code.label(dim_inst_hier_label.get('state_code', 'code_state')),
                                    dim_inst_hier.c.district_guid.label(dim_inst_hier_label.get('district_guid', 'name_distrct')),
                                    dim_inst_hier.c.district_name.label(dim_inst_hier_label.get('district_name', 'name_distrct')),
                                    dim_inst_hier.c.school_guid.label(dim_inst_hier_label.get('school_guid', 'guid_school')),
                                    dim_inst_hier.c.school_name.label(dim_inst_hier_label.get('school_name', 'name_school')),
                                    dim_inst_hier.c.school_category.label(dim_inst_hier_label.get('school_category', 'school_category')),
                                    dim_student.c.student_guid.label(dim_student_label.get('student_guid', 'guid_student')),
                                    dim_student.c.first_name.label(dim_student_label.get('first_name', 'student_first_name')),
                                    dim_student.c.middle_name.label(dim_student_label.get('middle_name', 'student_middle_name')),
                                    dim_student.c.last_name.label(dim_student_label.get('last_name', 'student_last_name')),
                                    dim_student.c.address_1.label(dim_student_label.get('address_1', 'address_1')),
                                    dim_student.c.address_2.label(dim_student_label.get('address_2', 'address_2')),
                                    dim_student.c.city.label(dim_student_label.get('city', 'city')),
                                    dim_student.c.zip_code.label(dim_student_label.get('zip_code', 'zip_code')),
                                    dim_student.c.gender.label(dim_student_label.get('gender', 'gender')),
                                    dim_student.c.email.label(dim_student_label.get('email', 'email')),
                                    dim_student.c.dob.label(dim_student_label.get('dob', 'dob')),
                                    fact_asmt_outcome.c.enrl_grade.label(fact_asmt_outcome_label.get('enrl_grade', 'enrollment_grade')),
                                    fact_asmt_outcome.c.date_taken.label(fact_asmt_outcome_label.get('date_taken', 'date_taken')),
                                    fact_asmt_outcome.c.asmt_score.label(fact_asmt_outcome_label.get('asmt_score', 'asmt_score')),
                                    fact_asmt_outcome.c.asmt_score_range_min.label(fact_asmt_outcome_label.get('asmt_score_range_min', 'asmt_score_range_min')),
                                    fact_asmt_outcome.c.asmt_score_range_max.label(fact_asmt_outcome_label.get('asmt_score_range_max', 'asmt_score_range_max')),
                                    fact_asmt_outcome.c.asmt_perf_lvl.label(fact_asmt_outcome_label.get('asmt_perf_lvl', 'asmt_perf_lvl')),
                                    fact_asmt_outcome.c.asmt_claim_1_score.label(fact_asmt_outcome_label.get('asmt_claim_1_score', 'asmt_claim_1_score')),
                                    fact_asmt_outcome.c.asmt_claim_1_score_range_min.label(fact_asmt_outcome_label.get('asmt_claim_1_score_range_min', 'asmt_claim_1_score_range_min')),
                                    fact_asmt_outcome.c.asmt_claim_1_score_range_max.label(fact_asmt_outcome_label.get('asmt_claim_1_score_range_max', 'asmt_claim_1_score_range_max')),
                                    fact_asmt_outcome.c.asmt_claim_2_score.label(fact_asmt_outcome_label.get('asmt_claim_2_score', 'asmt_claim_2_score')),
                                    fact_asmt_outcome.c.asmt_claim_2_score_range_min.label(fact_asmt_outcome_label.get('asmt_claim_2_score_range_min', 'asmt_claim_2_score_range_min')),
                                    fact_asmt_outcome.c.asmt_claim_2_score_range_max.label(fact_asmt_outcome_label.get('asmt_claim_2_score_range_max', 'asmt_claim_2_score_range_max')),
                                    fact_asmt_outcome.c.asmt_claim_3_score.label(fact_asmt_outcome_label.get('asmt_claim_3_score', 'asmt_claim_3_score')),
                                    fact_asmt_outcome.c.asmt_claim_3_score_range_min.label(fact_asmt_outcome_label.get('asmt_claim_3_score_range_min', 'asmt_claim_3_score_range_min')),
                                    fact_asmt_outcome.c.asmt_claim_3_score_range_max.label(fact_asmt_outcome_label.get('asmt_claim_3_score_range_max', 'asmt_claim_3_score_range_max')),
                                    fact_asmt_outcome.c.asmt_claim_4_score.label(fact_asmt_outcome_label.get('asmt_claim_4_score', 'asmt_claim_4_score')),
                                    fact_asmt_outcome.c.asmt_claim_4_score_range_min.label(fact_asmt_outcome_label.get('asmt_claim_4_score_range_min', 'asmt_claim_4_score_range_min')),
                                    fact_asmt_outcome.c.asmt_claim_4_score_range_max.label(fact_asmt_outcome_label.get('asmt_claim_4_score_range_max', 'asmt_claim_4_score_range_max')),
                                    fact_asmt_outcome.c.dmg_eth_hsp.label(fact_asmt_outcome_label.get('dmg_eth_hsp', 'dmg_eth_hsp')),
                                    fact_asmt_outcome.c.dmg_eth_ami.label(fact_asmt_outcome_label.get('dmg_eth_ami', 'dmg_eth_ami')),
                                    fact_asmt_outcome.c.dmg_eth_asn.label(fact_asmt_outcome_label.get('dmg_eth_asn', 'dmg_eth_asn')),
                                    fact_asmt_outcome.c.dmg_eth_blk.label(fact_asmt_outcome_label.get('dmg_eth_blk', 'dmg_eth_blk')),
                                    fact_asmt_outcome.c.dmg_eth_pcf.label(fact_asmt_outcome_label.get('dmg_eth_pcf', 'dmg_eth_pcf')),
                                    fact_asmt_outcome.c.dmg_eth_wht.label(fact_asmt_outcome_label.get('dmg_eth_wht', 'dmg_eth_wht')),
                                    fact_asmt_outcome.c.dmg_prg_iep.label(fact_asmt_outcome_label.get('dmg_prg_iep', 'dmg_prg_iep')),
                                    fact_asmt_outcome.c.dmg_prg_lep.label(fact_asmt_outcome_label.get('dmg_prg_lep', 'dmg_prg_lep')),
                                    fact_asmt_outcome.c.dmg_prg_504.label(fact_asmt_outcome_label.get('dmg_prg_504', 'dmg_prg_504')),
                                    fact_asmt_outcome.c.dmg_prg_tt1.label(fact_asmt_outcome_label.get('dmg_prg_tt1', 'dmg_prg_tt1')),
                                    fact_asmt_outcome.c.asmt_type.label(fact_asmt_outcome_label.get('asmt_type', 'asmt_type')),
                                    fact_asmt_outcome.c.asmt_year.label(fact_asmt_outcome_label.get('asmt_year', 'asmt_year')),
                                    fact_asmt_outcome.c.asmt_subject.label(fact_asmt_outcome_label.get('asmt_subject', 'asmt_subject'))],
                                    from_obj=[fact_asmt_outcome
                                              .join(dim_student, and_(dim_student.c.student_guid == fact_asmt_outcome.c.student_guid,
                                                                      dim_student.c.section_guid == fact_asmt_outcome.c.section_guid))
                                              .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_asmt_outcome.c.asmt_rec_id,
                                                                   dim_asmt.c.asmt_type == asmt_type))
                                              .join(dim_inst_hier, and_(dim_inst_hier.c.inst_hier_rec_id == fact_asmt_outcome.c.inst_hier_rec_id))])

        query = query.where(and_(fact_asmt_outcome.c.state_code == state_code))
        query = query.where(fact_asmt_outcome.c.asmt_type == asmt_type)
        if school_guid is not None:
            query = query.where(and_(fact_asmt_outcome.c.school_guid == school_guid))
        if district_guid is not None:
            query = query.where(and_(fact_asmt_outcome.c.district_guid == district_guid))
        if asmt_year is not None:
            query = query.where(and_(fact_asmt_outcome.c.asmt_year == asmt_year))
        if asmt_subject is not None:
            query = query.where(and_(fact_asmt_outcome.c.asmt_subject == asmt_subject))
        if asmt_grade is not None:
            query = query.where(and_(fact_asmt_outcome.c.asmt_grade == asmt_grade))

        query = query.order_by(dim_student.c.last_name).order_by(dim_student.c.first_name)
    return query
