'''
Created on Nov 1, 2013

@author: ejen
'''
from sqlalchemy.sql.expression import and_, func, literal

from edcore.database.edcore_connector import EdCoreDBConnection
from smarter.reports.helpers.constants import Constants
from smarter.security.context import select_with_context
from smarter.extracts.format import get_column_mapping
from smarter_common.security.constants import RolesConstants
from smarter.reports.helpers.filters import apply_filter_to_query
from smarter.extracts.constants import ExtractType


__permissions = {ExtractType.itemLevel: RolesConstants.ITEM_LEVEL_EXTRACTS,
                 ExtractType.rawData: RolesConstants.AUDIT_XML_EXTRACTS,
                 ExtractType.studentAssessment: RolesConstants.SAR_EXTRACTS}


def get_required_permission(extract_type):
    '''
    Queries are shared between different extracts, and permission is different based on the extract type
    The correct permission is returned given the extract type
    '''

    return __permissions.get(extract_type)


def get_extract_assessment_query(params):
    """
    private method to generate SQLAlchemy object or sql code for extraction

    :param params: for query parameters asmt_type, asmt_subject, asmt_year, limit
    """
    state_code = params.get(Constants.STATECODE)
    district_id = params.get(Constants.DISTRICTGUID)
    school_id = params.get(Constants.SCHOOLGUID)
    asmt_grade = params.get(Constants.ASMTGRADE)
    asmt_type = params.get(Constants.ASMTTYPE)
    asmt_year = params.get(Constants.ASMTYEAR)
    asmt_subject = params.get(Constants.ASMTSUBJECT)
    student = params.get(Constants.STUDENTGUID)

    dim_student_label = get_column_mapping(Constants.DIM_STUDENT)
    dim_inst_hier_label = get_column_mapping(Constants.DIM_INST_HIER)
    dim_asmt_label = get_column_mapping(Constants.DIM_ASMT)
    fact_asmt_outcome_vw_label = get_column_mapping(Constants.FACT_ASMT_OUTCOME_VW)

    with EdCoreDBConnection(state_code=state_code) as connector:
        dim_student = connector.get_table(Constants.DIM_STUDENT)
        dim_asmt = connector.get_table(Constants.DIM_ASMT)
        dim_inst_hier = connector.get_table(Constants.DIM_INST_HIER)
        fact_asmt_outcome_vw = connector.get_table(Constants.FACT_ASMT_OUTCOME_VW)
        # TODO: Look at removing dim_asmt
        query = select_with_context([dim_asmt.c.asmt_guid.label(dim_asmt_label.get(Constants.ASMT_GUID, Constants.ASMT_GUID)),
                                    fact_asmt_outcome_vw.c.where_taken_id.label(fact_asmt_outcome_vw_label.get('where_taken_id', 'guid_asmt_location')),
                                    fact_asmt_outcome_vw.c.where_taken_name.label(fact_asmt_outcome_vw_label.get('where_taken_name', 'name_asmt_location')),
                                    fact_asmt_outcome_vw.c.asmt_grade.label(fact_asmt_outcome_vw_label.get(Constants.ASMT_GRADE, Constants.ASMT_GRADE)),
                                    dim_inst_hier.c.state_code.label(dim_inst_hier_label.get(Constants.STATE_CODE, 'code_state')),
                                    dim_inst_hier.c.district_id.label(dim_inst_hier_label.get(Constants.DISTRICT_ID, 'name_distrct')),
                                    dim_inst_hier.c.district_name.label(dim_inst_hier_label.get(Constants.DISTRICT_NAME, 'name_distrct')),
                                    dim_inst_hier.c.school_id.label(dim_inst_hier_label.get(Constants.SCHOOL_ID, 'guid_school')),
                                    dim_inst_hier.c.school_name.label(dim_inst_hier_label.get(Constants.SCHOOL_NAME, 'name_school')),
                                    dim_student.c.student_id.label(dim_student_label.get(Constants.STUDENT_ID, 'guid_student')),
                                    dim_student.c.first_name.label(dim_student_label.get('first_name', 'first_name')),
                                    dim_student.c.middle_name.label(dim_student_label.get('middle_name', 'middle_name')),
                                    dim_student.c.last_name.label(dim_student_label.get('last_name', 'last_name')),
                                    dim_student.c.sex.label(dim_student_label.get('sex', 'sex')),
                                    dim_student.c.birthdate.label(dim_student_label.get('birthdate', 'dob')),
                                    dim_student.c.external_student_id.label(dim_student_label.get('external_student_id', 'external_student_id')),
                                    fact_asmt_outcome_vw.c.enrl_grade.label(fact_asmt_outcome_vw_label.get('enrl_grade', 'enrollment_grade')),
                                    dim_student.c.group_1_id.label(dim_student_label.get('group_1_id', 'group_1_id')),
                                    dim_student.c.group_1_text.label(dim_student_label.get('group_1_text', 'group_1_text')),
                                    dim_student.c.group_2_id.label(dim_student_label.get('group_2_id', 'group_2_id')),
                                    dim_student.c.group_2_text.label(dim_student_label.get('group_2_text', 'group_2_text')),
                                    dim_student.c.group_3_id.label(dim_student_label.get('group_3_id', 'group_3_id')),
                                    dim_student.c.group_3_text.label(dim_student_label.get('group_3_text', 'group_3_text')),
                                    dim_student.c.group_4_id.label(dim_student_label.get('group_4_id', 'group_4_id')),
                                    dim_student.c.group_4_text.label(dim_student_label.get('group_4_text', 'group_4_text')),
                                    dim_student.c.group_5_id.label(dim_student_label.get('group_5_id', 'group_5_id')),
                                    dim_student.c.group_5_text.label(dim_student_label.get('group_5_text', 'group_5_text')),
                                    dim_student.c.group_6_id.label(dim_student_label.get('group_6_id', 'group_6_id')),
                                    dim_student.c.group_6_text.label(dim_student_label.get('group_6_text', 'group_6_text')),
                                    dim_student.c.group_7_id.label(dim_student_label.get('group_7_id', 'group_7_id')),
                                    dim_student.c.group_7_text.label(dim_student_label.get('group_7_text', 'group_7_text')),
                                    dim_student.c.group_8_id.label(dim_student_label.get('group_8_id', 'group_8_id')),
                                    dim_student.c.group_8_text.label(dim_student_label.get('group_8_text', 'group_8_text')),
                                    dim_student.c.group_9_id.label(dim_student_label.get('group_9_id', 'group_9_id')),
                                    dim_student.c.group_9_text.label(dim_student_label.get('group_9_text', 'group_9_text')),
                                    dim_student.c.group_10_id.label(dim_student_label.get('group_10_id', 'group_10_id')),
                                    dim_student.c.group_10_text.label(dim_student_label.get('group_10_text', 'group_10_text')),
                                    fact_asmt_outcome_vw.c.date_taken.label(fact_asmt_outcome_vw_label.get('date_taken', 'date_taken')),
                                    fact_asmt_outcome_vw.c.asmt_score.label(fact_asmt_outcome_vw_label.get('asmt_score', 'asmt_score')),
                                    fact_asmt_outcome_vw.c.asmt_score_range_min.label(fact_asmt_outcome_vw_label.get('asmt_score_range_min', 'asmt_score_range_min')),
                                    fact_asmt_outcome_vw.c.asmt_score_range_max.label(fact_asmt_outcome_vw_label.get('asmt_score_range_max', 'asmt_score_range_max')),
                                    fact_asmt_outcome_vw.c.asmt_perf_lvl.label(fact_asmt_outcome_vw_label.get('asmt_perf_lvl', 'asmt_perf_lvl')),
                                    fact_asmt_outcome_vw.c.asmt_claim_1_score.label(fact_asmt_outcome_vw_label.get('asmt_claim_1_score', 'asmt_claim_1_score')),
                                    fact_asmt_outcome_vw.c.asmt_claim_1_perf_lvl.label(fact_asmt_outcome_vw_label.get('asmt_claim_1_perf_lvl', 'asmt_claim_1_perf_lvl')),
                                    fact_asmt_outcome_vw.c.asmt_claim_1_score_range_min.label(fact_asmt_outcome_vw_label.get('asmt_claim_1_score_range_min', 'asmt_claim_1_score_range_min')),
                                    fact_asmt_outcome_vw.c.asmt_claim_1_score_range_max.label(fact_asmt_outcome_vw_label.get('asmt_claim_1_score_range_max', 'asmt_claim_1_score_range_max')),
                                    fact_asmt_outcome_vw.c.asmt_claim_2_score.label(fact_asmt_outcome_vw_label.get('asmt_claim_2_score', 'asmt_claim_2_score')),
                                    fact_asmt_outcome_vw.c.asmt_claim_2_perf_lvl.label(fact_asmt_outcome_vw_label.get('asmt_claim_2_perf_lvl', 'asmt_claim_2_perf_lvl')),
                                    fact_asmt_outcome_vw.c.asmt_claim_2_score_range_min.label(fact_asmt_outcome_vw_label.get('asmt_claim_2_score_range_min', 'asmt_claim_2_score_range_min')),
                                    fact_asmt_outcome_vw.c.asmt_claim_2_score_range_max.label(fact_asmt_outcome_vw_label.get('asmt_claim_2_score_range_max', 'asmt_claim_2_score_range_max')),
                                    fact_asmt_outcome_vw.c.asmt_claim_3_score.label(fact_asmt_outcome_vw_label.get('asmt_claim_3_score', 'asmt_claim_3_score')),
                                    fact_asmt_outcome_vw.c.asmt_claim_3_perf_lvl.label(fact_asmt_outcome_vw_label.get('asmt_claim_3_perf_lvl', 'asmt_claim_3_perf_lvl')),
                                    fact_asmt_outcome_vw.c.asmt_claim_3_score_range_min.label(fact_asmt_outcome_vw_label.get('asmt_claim_3_score_range_min', 'asmt_claim_3_score_range_min')),
                                    fact_asmt_outcome_vw.c.asmt_claim_3_score_range_max.label(fact_asmt_outcome_vw_label.get('asmt_claim_3_score_range_max', 'asmt_claim_3_score_range_max')),
                                    fact_asmt_outcome_vw.c.asmt_claim_4_score.label(fact_asmt_outcome_vw_label.get('asmt_claim_4_score', 'asmt_claim_4_score')),
                                    fact_asmt_outcome_vw.c.asmt_claim_4_perf_lvl.label(fact_asmt_outcome_vw_label.get('asmt_claim_4_perf_lvl', 'asmt_claim_4_perf_lvl')),
                                    fact_asmt_outcome_vw.c.asmt_claim_4_score_range_min.label(fact_asmt_outcome_vw_label.get('asmt_claim_4_score_range_min', 'asmt_claim_4_score_range_min')),
                                    fact_asmt_outcome_vw.c.asmt_claim_4_score_range_max.label(fact_asmt_outcome_vw_label.get('asmt_claim_4_score_range_max', 'asmt_claim_4_score_range_max')),
                                    fact_asmt_outcome_vw.c.dmg_eth_hsp.label(fact_asmt_outcome_vw_label.get(Constants.DMG_ETH_HSP, Constants.DMG_ETH_HSP)),
                                    fact_asmt_outcome_vw.c.dmg_eth_ami.label(fact_asmt_outcome_vw_label.get(Constants.DMG_ETH_AMI, Constants.DMG_ETH_AMI)),
                                    fact_asmt_outcome_vw.c.dmg_eth_asn.label(fact_asmt_outcome_vw_label.get(Constants.DMG_ETH_ASN, Constants.DMG_ETH_ASN)),
                                    fact_asmt_outcome_vw.c.dmg_eth_blk.label(fact_asmt_outcome_vw_label.get(Constants.DMG_ETH_BLK, Constants.DMG_ETH_BLK)),
                                    fact_asmt_outcome_vw.c.dmg_eth_pcf.label(fact_asmt_outcome_vw_label.get(Constants.DMG_ETH_PCF, Constants.DMG_ETH_PCF)),
                                    fact_asmt_outcome_vw.c.dmg_eth_wht.label(fact_asmt_outcome_vw_label.get(Constants.DMG_ETH_WHT, Constants.DMG_ETH_WHT)),
                                    fact_asmt_outcome_vw.c.dmg_eth_2om.label(fact_asmt_outcome_vw_label.get(Constants.DMG_ETH_2OM, Constants.DMG_ETH_2OM)),
                                    fact_asmt_outcome_vw.c.dmg_prg_iep.label(fact_asmt_outcome_vw_label.get('dmg_prg_iep', 'dmg_prg_iep')),
                                    fact_asmt_outcome_vw.c.dmg_prg_lep.label(fact_asmt_outcome_vw_label.get('dmg_prg_lep', 'dmg_prg_lep')),
                                    fact_asmt_outcome_vw.c.dmg_prg_504.label(fact_asmt_outcome_vw_label.get('dmg_prg_504', 'dmg_prg_504')),
                                    fact_asmt_outcome_vw.c.dmg_sts_ecd.label(fact_asmt_outcome_vw_label.get('dmg_sts_ecd', 'dmg_sts_ecd')),
                                    fact_asmt_outcome_vw.c.dmg_sts_mig.label(fact_asmt_outcome_vw_label.get('dmg_sts_mig', 'dmg_sts_mig')),
                                    fact_asmt_outcome_vw.c.asmt_type.label(fact_asmt_outcome_vw_label.get(Constants.ASMT_TYPE, Constants.ASMT_TYPE)),
                                    fact_asmt_outcome_vw.c.asmt_year.label(fact_asmt_outcome_vw_label.get(Constants.ASMT_YEAR, Constants.ASMT_YEAR)),
                                    fact_asmt_outcome_vw.c.asmt_subject.label(fact_asmt_outcome_vw_label.get(Constants.ASMT_SUBJECT, Constants.ASMT_SUBJECT)),
                                    fact_asmt_outcome_vw.c.acc_asl_video_embed.label(fact_asmt_outcome_vw_label.get('acc_asl_video_embed', 'acc_asl_video_embed')),
                                    fact_asmt_outcome_vw.c.acc_noise_buffer_nonembed.label(fact_asmt_outcome_vw_label.get('acc_noise_buffer_nonembed', 'acc_noise_buffer_nonembed')),
                                    fact_asmt_outcome_vw.c.acc_print_on_demand_items_nonembed.label(fact_asmt_outcome_vw_label.get('acc_print_on_demand_items_nonembed', 'acc_print_on_demand_items_nonembed')),
                                    fact_asmt_outcome_vw.c.acc_braile_embed.label(fact_asmt_outcome_vw_label.get('acc_braile_embed', 'acc_braile_embed')),
                                    fact_asmt_outcome_vw.c.acc_closed_captioning_embed.label(fact_asmt_outcome_vw_label.get('acc_closed_captioning_embed', 'acc_closed_captioning_embed')),
                                    fact_asmt_outcome_vw.c.acc_text_to_speech_embed.label(fact_asmt_outcome_vw_label.get('acc_text_to_speech_embed', 'acc_text_to_speech_embed')),
                                    fact_asmt_outcome_vw.c.acc_abacus_nonembed.label(fact_asmt_outcome_vw_label.get('acc_abacus_nonembed', 'acc_abacus_nonembed')),
                                    fact_asmt_outcome_vw.c.acc_alternate_response_options_nonembed.label(fact_asmt_outcome_vw_label.get('acc_alternate_response_options_nonembed', 'acc_alternate_response_options_nonembed')),
                                    fact_asmt_outcome_vw.c.acc_calculator_nonembed.label(fact_asmt_outcome_vw_label.get('acc_calculator_nonembed', 'acc_calculator_nonembed')),
                                    fact_asmt_outcome_vw.c.acc_multiplication_table_nonembed.label(fact_asmt_outcome_vw_label.get('acc_multiplication_table_nonembed', 'acc_multiplication_table_nonembed')),
                                    fact_asmt_outcome_vw.c.acc_print_on_demand_nonembed.label(fact_asmt_outcome_vw_label.get('acc_print_on_demand_nonembed', 'acc_print_on_demand_nonembed')),
                                    fact_asmt_outcome_vw.c.acc_read_aloud_nonembed.label(fact_asmt_outcome_vw_label.get('acc_read_aloud_nonembed', 'acc_read_aloud_nonembed')),
                                    fact_asmt_outcome_vw.c.acc_scribe_nonembed.label(fact_asmt_outcome_vw_label.get('acc_scribe_nonembed', 'acc_scribe_nonembed')),
                                    fact_asmt_outcome_vw.c.acc_speech_to_text_nonembed.label(fact_asmt_outcome_vw_label.get('acc_speech_to_text_nonembed', 'acc_speech_to_text_nonembed')),
                                    fact_asmt_outcome_vw.c.acc_streamline_mode.label(fact_asmt_outcome_vw_label.get('acc_streamline_mode', 'acc_streamline_mode'))],
                                    from_obj=[fact_asmt_outcome_vw
                                              .join(dim_student, and_(fact_asmt_outcome_vw.c.student_rec_id == dim_student.c.student_rec_id))
                                              .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_asmt_outcome_vw.c.asmt_rec_id,
                                                                   dim_asmt.c.asmt_type == asmt_type))
                                              .join(dim_inst_hier, and_(dim_inst_hier.c.inst_hier_rec_id == fact_asmt_outcome_vw.c.inst_hier_rec_id))], permission=RolesConstants.SAR_EXTRACTS, state_code=state_code)

        query = query.where(and_(fact_asmt_outcome_vw.c.state_code == state_code))
        query = query.where(and_(fact_asmt_outcome_vw.c.asmt_type == asmt_type))
        query = query.where(and_(fact_asmt_outcome_vw.c.rec_status == Constants.CURRENT))
        if school_id is not None:
            query = query.where(and_(fact_asmt_outcome_vw.c.school_id == school_id))
        if district_id is not None:
            query = query.where(and_(fact_asmt_outcome_vw.c.district_id == district_id))
        if asmt_year is not None:
            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_year == asmt_year))
        if asmt_subject is not None:
            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_subject == asmt_subject))
        if asmt_grade is not None:
            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_grade == asmt_grade))
        if student:
            query = query.where(and_(fact_asmt_outcome_vw.c.student_id.in_(student)))

        query = apply_filter_to_query(query, fact_asmt_outcome_vw, dim_student, params)
        query = query.order_by(dim_student.c.last_name).order_by(dim_student.c.first_name)
    return query


def get_extract_assessment_query_iab(params):
    """
    private method to generate SQLAlchemy object or sql code for extraction

    :param params: for query parameters asmt_type, asmt_subject, asmt_year, limit
    """
    state_code = params.get(Constants.STATECODE)
    district_id = params.get(Constants.DISTRICTGUID)
    school_id = params.get(Constants.SCHOOLGUID)
    asmt_grade = params.get(Constants.ASMTGRADE)
    asmt_type = params.get(Constants.ASMTTYPE)
    asmt_year = params.get(Constants.ASMTYEAR)
    asmt_subject = params.get(Constants.ASMTSUBJECT)
    student = params.get(Constants.STUDENTGUID)

    dim_student_label = get_column_mapping(Constants.DIM_STUDENT)
    dim_inst_hier_label = get_column_mapping(Constants.DIM_INST_HIER)
    dim_asmt_label = get_column_mapping(Constants.DIM_ASMT)
    fact_block_asmt_outcome_label = get_column_mapping(Constants.FACT_BLOCK_ASMT_OUTCOME)
    fact_asmt_outcome_vw_label = get_column_mapping(Constants.FACT_ASMT_OUTCOME_VW)

    with EdCoreDBConnection(state_code=state_code) as connector:
        dim_student = connector.get_table(Constants.DIM_STUDENT)
        dim_asmt = connector.get_table(Constants.DIM_ASMT)
        dim_inst_hier = connector.get_table(Constants.DIM_INST_HIER)
        fact_block_asmt_outcome = connector.get_table(Constants.FACT_BLOCK_ASMT_OUTCOME)
        # TODO: Look at removing dim_asmt
        query = select_with_context([dim_asmt.c.asmt_guid.label(dim_asmt_label.get(Constants.ASMT_GUID, Constants.ASMT_GUID)),
                                    fact_block_asmt_outcome.c.where_taken_id.label(fact_block_asmt_outcome_label.get('where_taken_id', 'guid_asmt_location')),
                                    fact_block_asmt_outcome.c.where_taken_name.label(fact_block_asmt_outcome_label.get('where_taken_name', 'name_asmt_location')),
                                    fact_block_asmt_outcome.c.asmt_grade.label(fact_block_asmt_outcome_label.get(Constants.ASMT_GRADE, Constants.ASMT_GRADE)),
                                    dim_inst_hier.c.state_code.label(dim_inst_hier_label.get(Constants.STATE_CODE, 'code_state')),
                                    dim_inst_hier.c.district_id.label(dim_inst_hier_label.get(Constants.DISTRICT_ID, 'name_distrct')),
                                    dim_inst_hier.c.district_name.label(dim_inst_hier_label.get(Constants.DISTRICT_NAME, 'name_distrct')),
                                    dim_inst_hier.c.school_id.label(dim_inst_hier_label.get(Constants.SCHOOL_ID, 'guid_school')),
                                    dim_inst_hier.c.school_name.label(dim_inst_hier_label.get(Constants.SCHOOL_NAME, 'name_school')),
                                    dim_student.c.student_id.label(dim_student_label.get(Constants.STUDENT_ID, 'guid_student')),
                                    dim_student.c.first_name.label(dim_student_label.get('first_name', 'first_name')),
                                    dim_student.c.middle_name.label(dim_student_label.get('middle_name', 'middle_name')),
                                    dim_student.c.last_name.label(dim_student_label.get('last_name', 'last_name')),
                                    dim_student.c.sex.label(dim_student_label.get('sex', 'sex')),
                                    dim_student.c.birthdate.label(dim_student_label.get('birthdate', 'dob')),
                                    dim_student.c.external_student_id.label(dim_student_label.get('external_student_id', 'external_student_id')),
                                    fact_block_asmt_outcome.c.enrl_grade.label(fact_block_asmt_outcome_label.get('enrl_grade', 'enrollment_grade')),
                                    dim_student.c.group_1_id.label(dim_student_label.get('group_1_id', 'group_1_id')),
                                    dim_student.c.group_1_text.label(dim_student_label.get('group_1_text', 'group_1_text')),
                                    dim_student.c.group_2_id.label(dim_student_label.get('group_2_id', 'group_2_id')),
                                    dim_student.c.group_2_text.label(dim_student_label.get('group_2_text', 'group_2_text')),
                                    dim_student.c.group_3_id.label(dim_student_label.get('group_3_id', 'group_3_id')),
                                    dim_student.c.group_3_text.label(dim_student_label.get('group_3_text', 'group_3_text')),
                                    dim_student.c.group_4_id.label(dim_student_label.get('group_4_id', 'group_4_id')),
                                    dim_student.c.group_4_text.label(dim_student_label.get('group_4_text', 'group_4_text')),
                                    dim_student.c.group_5_id.label(dim_student_label.get('group_5_id', 'group_5_id')),
                                    dim_student.c.group_5_text.label(dim_student_label.get('group_5_text', 'group_5_text')),
                                    dim_student.c.group_6_id.label(dim_student_label.get('group_6_id', 'group_6_id')),
                                    dim_student.c.group_6_text.label(dim_student_label.get('group_6_text', 'group_6_text')),
                                    dim_student.c.group_7_id.label(dim_student_label.get('group_7_id', 'group_7_id')),
                                    dim_student.c.group_7_text.label(dim_student_label.get('group_7_text', 'group_7_text')),
                                    dim_student.c.group_8_id.label(dim_student_label.get('group_8_id', 'group_8_id')),
                                    dim_student.c.group_8_text.label(dim_student_label.get('group_8_text', 'group_8_text')),
                                    dim_student.c.group_9_id.label(dim_student_label.get('group_9_id', 'group_9_id')),
                                    dim_student.c.group_9_text.label(dim_student_label.get('group_9_text', 'group_9_text')),
                                    dim_student.c.group_10_id.label(dim_student_label.get('group_10_id', 'group_10_id')),
                                    dim_student.c.group_10_text.label(dim_student_label.get('group_10_text', 'group_10_text')),
                                    fact_block_asmt_outcome.c.date_taken.label(fact_block_asmt_outcome_label.get('date_taken', 'date_taken')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_score', 'asmt_score')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_score_range_min', 'asmt_score_range_min')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_score_range_max', 'asmt_score_range_max')),
                                    fact_block_asmt_outcome.c.asmt_perf_lvl.label(fact_block_asmt_outcome_label.get('asmt_perf_lvl', 'asmt_perf_lvl')),
                                    fact_block_asmt_outcome.c.asmt_claim_1_score.label(fact_block_asmt_outcome_label.get('asmt_claim_1_score', 'asmt_claim_1_score')),
                                    fact_block_asmt_outcome.c.asmt_claim_1_perf_lvl.label(fact_block_asmt_outcome_label.get('asmt_claim_1_perf_lvl', 'asmt_claim_1_perf_lvl')),
                                    fact_block_asmt_outcome.c.asmt_claim_1_score_range_min.label(fact_block_asmt_outcome_label.get('asmt_claim_1_score_range_min', 'asmt_claim_1_score_range_min')),
                                    fact_block_asmt_outcome.c.asmt_claim_1_score_range_max.label(fact_block_asmt_outcome_label.get('asmt_claim_1_score_range_max', 'asmt_claim_1_score_range_max')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_claim_2_score', 'asmt_claim_2_score')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_claim_2_perf_lvl', 'asmt_claim_2_perf_lvl')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_claim_2_score_range_min', 'asmt_claim_2_score_range_min')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_claim_2_score_range_max', 'asmt_claim_2_score_range_max')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_claim_3_score', 'asmt_claim_3_score')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_claim_3_perf_lvl', 'asmt_claim_3_perf_lvl')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_claim_3_score_range_min', 'asmt_claim_3_score_range_min')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_claim_3_score_range_max', 'asmt_claim_3_score_range_max')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_claim_4_score', 'asmt_claim_4_score')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_claim_4_perf_lvl', 'asmt_claim_4_perf_lvl')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_claim_4_score_range_min', 'asmt_claim_4_score_range_min')),
                                    literal("").label(fact_asmt_outcome_vw_label.get('asmt_claim_4_score_range_max', 'asmt_claim_4_score_range_max')),
                                    fact_block_asmt_outcome.c.dmg_eth_hsp.label(fact_block_asmt_outcome_label.get(Constants.DMG_ETH_HSP, Constants.DMG_ETH_HSP)),
                                    fact_block_asmt_outcome.c.dmg_eth_ami.label(fact_block_asmt_outcome_label.get(Constants.DMG_ETH_AMI, Constants.DMG_ETH_AMI)),
                                    fact_block_asmt_outcome.c.dmg_eth_asn.label(fact_block_asmt_outcome_label.get(Constants.DMG_ETH_ASN, Constants.DMG_ETH_ASN)),
                                    fact_block_asmt_outcome.c.dmg_eth_blk.label(fact_block_asmt_outcome_label.get(Constants.DMG_ETH_BLK, Constants.DMG_ETH_BLK)),
                                    fact_block_asmt_outcome.c.dmg_eth_pcf.label(fact_block_asmt_outcome_label.get(Constants.DMG_ETH_PCF, Constants.DMG_ETH_PCF)),
                                    fact_block_asmt_outcome.c.dmg_eth_wht.label(fact_block_asmt_outcome_label.get(Constants.DMG_ETH_WHT, Constants.DMG_ETH_WHT)),
                                    fact_block_asmt_outcome.c.dmg_eth_2om.label(fact_block_asmt_outcome_label.get(Constants.DMG_ETH_2OM, Constants.DMG_ETH_2OM)),
                                    fact_block_asmt_outcome.c.dmg_prg_iep.label(fact_block_asmt_outcome_label.get('dmg_prg_iep', 'dmg_prg_iep')),
                                    fact_block_asmt_outcome.c.dmg_prg_lep.label(fact_block_asmt_outcome_label.get('dmg_prg_lep', 'dmg_prg_lep')),
                                    fact_block_asmt_outcome.c.dmg_prg_504.label(fact_block_asmt_outcome_label.get('dmg_prg_504', 'dmg_prg_504')),
                                    fact_block_asmt_outcome.c.dmg_sts_ecd.label(fact_block_asmt_outcome_label.get('dmg_sts_ecd', 'dmg_sts_ecd')),
                                    fact_block_asmt_outcome.c.dmg_sts_mig.label(fact_block_asmt_outcome_label.get('dmg_sts_mig', 'dmg_sts_mig')),
                                    fact_block_asmt_outcome.c.asmt_type.label(fact_block_asmt_outcome_label.get(Constants.ASMT_TYPE, Constants.ASMT_TYPE)),
                                    fact_block_asmt_outcome.c.asmt_year.label(fact_block_asmt_outcome_label.get(Constants.ASMT_YEAR, Constants.ASMT_YEAR)),
                                    fact_block_asmt_outcome.c.asmt_subject.label(fact_block_asmt_outcome_label.get(Constants.ASMT_SUBJECT, Constants.ASMT_SUBJECT)),
                                    fact_block_asmt_outcome.c.acc_asl_video_embed.label(fact_block_asmt_outcome_label.get('acc_asl_video_embed', 'acc_asl_video_embed')),
                                    fact_block_asmt_outcome.c.acc_noise_buffer_nonembed.label(fact_block_asmt_outcome_label.get('acc_noise_buffer_nonembed', 'acc_noise_buffer_nonembed')),
                                    fact_block_asmt_outcome.c.acc_print_on_demand_items_nonembed.label(fact_block_asmt_outcome_label.get('acc_print_on_demand_items_nonembed', 'acc_print_on_demand_items_nonembed')),
                                    fact_block_asmt_outcome.c.acc_braile_embed.label(fact_block_asmt_outcome_label.get('acc_braile_embed', 'acc_braile_embed')),
                                    fact_block_asmt_outcome.c.acc_closed_captioning_embed.label(fact_block_asmt_outcome_label.get('acc_closed_captioning_embed', 'acc_closed_captioning_embed')),
                                    fact_block_asmt_outcome.c.acc_text_to_speech_embed.label(fact_block_asmt_outcome_label.get('acc_text_to_speech_embed', 'acc_text_to_speech_embed')),
                                    fact_block_asmt_outcome.c.acc_abacus_nonembed.label(fact_block_asmt_outcome_label.get('acc_abacus_nonembed', 'acc_abacus_nonembed')),
                                    fact_block_asmt_outcome.c.acc_alternate_response_options_nonembed.label(fact_block_asmt_outcome_label.get('acc_alternate_response_options_nonembed', 'acc_alternate_response_options_nonembed')),
                                    fact_block_asmt_outcome.c.acc_calculator_nonembed.label(fact_block_asmt_outcome_label.get('acc_calculator_nonembed', 'acc_calculator_nonembed')),
                                    fact_block_asmt_outcome.c.acc_multiplication_table_nonembed.label(fact_block_asmt_outcome_label.get('acc_multiplication_table_nonembed', 'acc_multiplication_table_nonembed')),
                                    fact_block_asmt_outcome.c.acc_print_on_demand_nonembed.label(fact_block_asmt_outcome_label.get('acc_print_on_demand_nonembed', 'acc_print_on_demand_nonembed')),
                                    fact_block_asmt_outcome.c.acc_read_aloud_nonembed.label(fact_block_asmt_outcome_label.get('acc_read_aloud_nonembed', 'acc_read_aloud_nonembed')),
                                    fact_block_asmt_outcome.c.acc_scribe_nonembed.label(fact_block_asmt_outcome_label.get('acc_scribe_nonembed', 'acc_scribe_nonembed')),
                                    fact_block_asmt_outcome.c.acc_speech_to_text_nonembed.label(fact_block_asmt_outcome_label.get('acc_speech_to_text_nonembed', 'acc_speech_to_text_nonembed')),
                                    fact_block_asmt_outcome.c.acc_streamline_mode.label(fact_block_asmt_outcome_label.get('acc_streamline_mode', 'acc_streamline_mode'))],
                                    from_obj=[fact_block_asmt_outcome
                                              .join(dim_student, and_(fact_block_asmt_outcome.c.student_rec_id == dim_student.c.student_rec_id))
                                              .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_block_asmt_outcome.c.asmt_rec_id,
                                                                   dim_asmt.c.asmt_type == asmt_type))
                                              .join(dim_inst_hier, and_(dim_inst_hier.c.inst_hier_rec_id == fact_block_asmt_outcome.c.inst_hier_rec_id))], permission=RolesConstants.SAR_EXTRACTS, state_code=state_code)

        query = query.where(and_(fact_block_asmt_outcome.c.state_code == state_code))
        query = query.where(and_(fact_block_asmt_outcome.c.asmt_type == asmt_type))
        query = query.where(and_(fact_block_asmt_outcome.c.rec_status == Constants.CURRENT))
        if school_id is not None:
            query = query.where(and_(fact_block_asmt_outcome.c.school_id == school_id))
        if district_id is not None:
            query = query.where(and_(fact_block_asmt_outcome.c.district_id == district_id))
        if asmt_year is not None:
            query = query.where(and_(fact_block_asmt_outcome.c.asmt_year == asmt_year))
        if asmt_subject is not None:
            query = query.where(and_(fact_block_asmt_outcome.c.asmt_subject == asmt_subject))
        if asmt_grade is not None:
            query = query.where(and_(fact_block_asmt_outcome.c.asmt_grade == asmt_grade))
        if student:
            query = query.where(and_(fact_block_asmt_outcome.c.student_id.in_(student)))

        query = apply_filter_to_query(query, fact_block_asmt_outcome, dim_student, params)
        query = query.order_by(dim_student.c.last_name).order_by(dim_student.c.first_name)
    return query


def get_extract_assessment_item_and_raw_count_query(params, extract_type):
    """
    private method to generate SQLAlchemy object or sql code for extraction of students for item level/raw data

    :param params: for query parameters asmt_year, asmt_type, asmt_subject, asmt_grade
    """
    state_code = params.get(Constants.STATECODE)

    with EdCoreDBConnection(state_code=state_code) as connector:
        fact_asmt_outcome_vw = connector.get_table(Constants.FACT_ASMT_OUTCOME_VW)
        query = select_with_context([func.count().label(Constants.COUNT)],
                                    from_obj=[fact_asmt_outcome_vw],
                                    permission=get_required_permission(extract_type),
                                    state_code=state_code)

        query = _assessment_item_and_raw_where_clause_builder(query, fact_asmt_outcome_vw, params)
    return query


def get_extract_assessment_item_and_raw_query(params, extract_type):
    """
    private method to generate SQLAlchemy object or sql code for extraction of students for item level/raw data

    :param params: for query parameters asmt_year, asmt_type, asmt_subject, asmt_grade
    """
    state_code = params.get(Constants.STATECODE)

    with EdCoreDBConnection(state_code=state_code) as connector:
        dim_asmt = connector.get_table(Constants.DIM_ASMT)
        fact_asmt_outcome_vw = connector.get_table(Constants.FACT_ASMT_OUTCOME_VW)
        # TODO: Look at removing dim_asmt
        query = select_with_context([fact_asmt_outcome_vw.c.state_code,
                                     fact_asmt_outcome_vw.c.asmt_year,
                                     fact_asmt_outcome_vw.c.asmt_type,
                                     dim_asmt.c.effective_date,
                                     fact_asmt_outcome_vw.c.asmt_subject,
                                     fact_asmt_outcome_vw.c.asmt_grade,
                                     fact_asmt_outcome_vw.c.district_id,
                                     fact_asmt_outcome_vw.c.student_id],
                                    from_obj=[fact_asmt_outcome_vw
                                              .join(dim_asmt, and_(dim_asmt.c.asmt_rec_id == fact_asmt_outcome_vw.c.asmt_rec_id))],
                                    permission=get_required_permission(extract_type),
                                    state_code=state_code)
        query = _assessment_item_and_raw_where_clause_builder(query, fact_asmt_outcome_vw, params)
    return query


def _assessment_item_and_raw_where_clause_builder(query, fact_asmt_outcome_vw, params):
    state_code = params.get(Constants.STATECODE)
    asmt_year = params.get(Constants.ASMTYEAR)
    asmt_type = params.get(Constants.ASMTTYPE)
    asmt_subject = params.get(Constants.ASMTSUBJECT)
    asmt_grade = params.get(Constants.ASMTGRADE)
    query = query.where(and_(fact_asmt_outcome_vw.c.state_code == state_code, fact_asmt_outcome_vw.c.asmt_year == asmt_year,
                             fact_asmt_outcome_vw.c.asmt_type == asmt_type, fact_asmt_outcome_vw.c.asmt_subject == asmt_subject,
                             fact_asmt_outcome_vw.c.asmt_grade == asmt_grade, fact_asmt_outcome_vw.c.rec_status == Constants.CURRENT))
    query = apply_filter_to_query(query, fact_asmt_outcome_vw, None, params)  # Filters demographics
    return query
