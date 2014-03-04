from datetime import datetime
from sqlalchemy.schema import MetaData, Sequence
from sqlalchemy import Table, Column, text
from sqlalchemy.types import Text, Boolean, TIMESTAMP, Interval, TIME
from sqlalchemy.types import BigInteger, SmallInteger, String, Float


def generate_udl2_metadata(schema_name=None, bind=None):
    '''
    generate_udl2_metadata function creates a metadata object that contains all udl2 related staging tables.
    '''

    metadata = MetaData(schema=schema_name, bind=bind)

    stg_mock_load = Table('STG_MOCK_LOAD', metadata,
                          Column('record_sid', BigInteger, primary_key=True),
                          Column('guid_batch', String(256), nullable=False),
                          Column('substr_test', String(256), nullable=False),
                          Column('number_test', String(256), nullable=False),
                          )

    int_mock_load = Table('INT_MOCK_LOAD', metadata,
                          Column('record_sid', BigInteger, primary_key=True),
                          Column('guid_batch', String(256), nullable=False),
                          Column('substr_test', String(256), nullable=False),
                          Column('number_test', String(256), nullable=False),
                          )

    udl_batch = Table('UDL_BATCH', metadata,
                      Column('batch_sid', BigInteger, primary_key=True),
                      Column('guid_batch', String(256), nullable=False),
                      Column('load_type', String(50), nullable=True),
                      Column('working_schema', String(50), nullable=True),
                      Column('udl_phase', String(256), nullable=True),
                      Column('udl_phase_step', String(50), nullable=True),
                      Column('udl_phase_step_status', String(50), nullable=True),
                      Column('error_desc', Text, nullable=True),
                      Column('stack_trace', Text, nullable=True),
                      Column('udl_leaf', Boolean, nullable=True),
                      Column('size_records', BigInteger, nullable=True),
                      Column('size_units', BigInteger, nullable=True),
                      Column('start_timestamp', TIMESTAMP, nullable=True, server_default=text('NOW()')),
                      Column('end_timestamp', TIMESTAMP, nullable=True, server_default=text('NOW()')),
                      Column('duration', Interval, nullable=True),
                      Column('time_for_one_million_records', TIME, nullable=True),
                      Column('records_per_hour', BigInteger, nullable=True),
                      Column('task_id', String(256), nullable=True),
                      Column('task_status_url', String(256), nullable=True),
                      Column('user_sid', BigInteger, nullable=True),
                      Column('user_email', String(256), nullable=True),
                      Column('created_date', TIMESTAMP, nullable=True, server_default=text('NOW()')),
                      Column('mod_date', TIMESTAMP, nullable=False, server_default=text('NOW()')),
                      )

    stg_sbac_stu_reg = Table('STG_SBAC_STU_REG', metadata,
                             Column('record_sid', BigInteger, primary_key=True),
                             Column('guid_batch', String(256), nullable=False),
                             Column('src_file_rec_num', BigInteger, nullable=True),
                             Column('name_state', String(256), nullable=True),
                             Column('code_state', String(256), nullable=True),
                             Column('guid_district', String(256), nullable=True),
                             Column('name_district', String(256), nullable=True),
                             Column('guid_school', String(256), nullable=True),
                             Column('name_school', String(256), nullable=True),
                             Column('guid_student', String(256), nullable=True),
                             Column('external_ssid_student', String(256), nullable=True),
                             Column('name_student_first', String(256), nullable=True),
                             Column('name_student_middle', String(256), nullable=True),
                             Column('name_student_last', String(256), nullable=True),
                             Column('gender_student', String(256), nullable=True),
                             Column('dob_student', String(256), nullable=True),
                             Column('grade_enrolled', String(256), nullable=True),
                             Column('dmg_eth_hsp', String(256), nullable=True),
                             Column('dmg_eth_ami', String(256), nullable=True),
                             Column('dmg_eth_asn', String(256), nullable=True),
                             Column('dmg_eth_blk', String(256), nullable=True),
                             Column('dmg_eth_pcf', String(256), nullable=True),
                             Column('dmg_eth_wht', String(256), nullable=True),
                             Column('dmg_prg_iep', String(256), nullable=True),
                             Column('dmg_prg_lep', String(256), nullable=True),
                             Column('dmg_prg_504', String(256), nullable=True),
                             Column('dmg_sts_ecd', String(256), nullable=True),
                             Column('dmg_sts_mig', String(256), nullable=True),
                             Column('dmg_multi_race', String(256), nullable=True),
                             Column('code_confirm', String(256), nullable=True),
                             Column('code_language', String(256), nullable=True),
                             Column('eng_prof_lvl', String(256), nullable=True),
                             Column('us_school_entry_date', String(256), nullable=True),
                             Column('lep_entry_date', String(256), nullable=True),
                             Column('lep_exit_date', String(256), nullable=True),
                             Column('t3_program_type', String(256), nullable=True),
                             Column('prim_disability_type', String(256), nullable=True),
                             Column('created_date', TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()')),
                             )

    stg_sbac_asmt_outcome = Table('STG_SBAC_ASMT_OUTCOME', metadata,
                                  Column('record_sid', BigInteger, primary_key=True),
                                  Column('op', String(1), nullable=True, server_default='C'),
                                  Column('guid_batch', String(256), nullable=False),
                                  Column('src_file_rec_num', BigInteger, nullable=True),
                                  Column('guid_asmt', String(256), nullable=True),
                                  Column('guid_asmt_location', String(256), nullable=True),
                                  Column('name_asmt_location', String(256), nullable=True),
                                  Column('grade_asmt', String(256), nullable=True),
                                  Column('name_state', String(256), nullable=True),
                                  Column('code_state', String(256), nullable=True),
                                  Column('guid_district', String(256), nullable=True),
                                  Column('name_district', String(256), nullable=True),
                                  Column('guid_school', String(256), nullable=True),
                                  Column('name_school', String(256), nullable=True),
                                  Column('type_school', String(256), nullable=True),
                                  Column('guid_student', String(256), nullable=True),
                                  Column('external_student_id', String(256), nullable=True),
                                  Column('name_student_first', String(256), nullable=True),
                                  Column('name_student_middle', String(256), nullable=True),
                                  Column('name_student_last', String(256), nullable=True),
                                  Column('address_student_line1', String(256), nullable=True),
                                  Column('address_student_line2', String(256), nullable=True),
                                  Column('address_student_city', String(256), nullable=True),
                                  Column('address_student_zip', String(256), nullable=True),
                                  Column('gender_student', String(256), nullable=True),
                                  Column('email_student', String(256), nullable=True),
                                  Column('dob_student', String(256), nullable=True),
                                  Column('grade_enrolled', String(256), nullable=True),
                                  Column('dmg_eth_hsp', String(256), nullable=True),
                                  Column('dmg_eth_ami', String(256), nullable=True),
                                  Column('dmg_eth_asn', String(256), nullable=True),
                                  Column('dmg_eth_blk', String(256), nullable=True),
                                  Column('dmg_eth_pcf', String(256), nullable=True),
                                  Column('dmg_eth_wht', String(256), nullable=True),
                                  Column('dmg_prg_iep', String(256), nullable=True),
                                  Column('dmg_prg_lep', String(256), nullable=True),
                                  Column('dmg_prg_504', String(256), nullable=True),
                                  Column('dmg_prg_tt1', String(256), nullable=True),
                                  Column('date_assessed', String(256), nullable=True),
                                  Column('score_asmt', String(256), nullable=True),
                                  Column('score_asmt_min', String(256), nullable=True),
                                  Column('score_asmt_max', String(256), nullable=True),
                                  Column('score_perf_level', String(256), nullable=True),
                                  Column('score_claim_1', String(256), nullable=True),
                                  Column('score_claim_1_min', String(256), nullable=True),
                                  Column('score_claim_1_max', String(256), nullable=True),
                                  Column('asmt_claim_1_perf_lvl', String(256), nullable=True),
                                  Column('score_claim_2', String(256), nullable=True),
                                  Column('score_claim_2_min', String(256), nullable=True),
                                  Column('score_claim_2_max', String(256), nullable=True),
                                  Column('asmt_claim_2_perf_lvl', String(256), nullable=True),
                                  Column('score_claim_3', String(256), nullable=True),
                                  Column('score_claim_3_min', String(256), nullable=True),
                                  Column('score_claim_3_max', String(256), nullable=True),
                                  Column('asmt_claim_3_perf_lvl', String(256), nullable=True),
                                  Column('score_claim_4', String(256), nullable=True),
                                  Column('score_claim_4_min', String(256), nullable=True),
                                  Column('score_claim_4_max', String(256), nullable=True),
                                  Column('asmt_claim_4_perf_lvl', String(256), nullable=True),
                                  Column('asmt_type', String(256), nullable=True),
                                  Column('asmt_subject', String(256), nullable=True),
                                  Column('asmt_year', String(256), nullable=True),
                                  Column('created_date', TIMESTAMP, nullable=False, server_default=text('NOW()')),
                                  Column('acc_asl_video_embed', String(256), nullable=False),
                                  Column('acc_asl_human_nonembed', String(256), nullable=False),
                                  Column('acc_braile_embed', String(256), nullable=False),
                                  Column('acc_closed_captioning_embed', String(256), nullable=False),
                                  Column('acc_text_to_speech_embed', String(256), nullable=False),
                                  Column('acc_abacus_nonembed', String(256), nullable=False),
                                  Column('acc_alternate_response_options_nonembed', String(256), nullable=False),
                                  Column('acc_calculator_nonembed', String(256), nullable=False),
                                  Column('acc_multiplication_table_nonembed', String(256), nullable=False),
                                  Column('acc_print_on_demand_nonembed', String(256), nullable=False),
                                  Column('acc_read_aloud_nonembed', String(256), nullable=False),
                                  Column('acc_scribe_nonembed', String(256), nullable=False),
                                  Column('acc_speech_to_text_nonembed', String(256), nullable=False),
                                  Column('acc_streamline_mode', String(256), nullable=False),
                                  )

    err_list = Table('ERR_LIST', metadata,
                     Column('record_sid', BigInteger, primary_key=True, nullable=False),
                     Column('guid_batch', String(256), primary_key=True, nullable=False),
                     Column('err_code', BigInteger, nullable=True),
                     Column('err_source', BigInteger, nullable=True),
                     Column('created_date', TIMESTAMP, nullable=False, server_default=text('NOW()')),
                     Column('err_input', Text, nullable=False, server_default='')
                     )

    int_sbac_asmt = Table('INT_SBAC_ASMT', metadata,
                          Column('record_sid', BigInteger, primary_key=True),
                          Column('guid_batch', String(256), nullable=False),
                          Column('guid_asmt', String(50), nullable=False),
                          Column('type', String(32), nullable=False),
                          Column('period', String(32), nullable=False),
                          Column('year', SmallInteger, nullable=False),
                          Column('version', String(16), nullable=False),
                          Column('subject', String(100), nullable=True),
                          Column('score_overall_min', SmallInteger, nullable=True),
                          Column('score_overall_max', SmallInteger, nullable=True),
                          Column('name_claim_1', String(256), nullable=True),
                          Column('score_claim_1_min', SmallInteger, nullable=True),
                          Column('score_claim_1_max', SmallInteger, nullable=True),
                          Column('score_claim_1_weight', Float, nullable=True),
                          Column('name_claim_2', String(256), nullable=True),
                          Column('score_claim_2_min', SmallInteger, nullable=True),
                          Column('score_claim_2_max', SmallInteger, nullable=True),
                          Column('score_claim_2_weight', Float, nullable=True),
                          Column('name_claim_3', String(256), nullable=True),
                          Column('score_claim_3_min', SmallInteger, nullable=True),
                          Column('score_claim_3_max', SmallInteger, nullable=True),
                          Column('score_claim_3_weight', Float, nullable=True),
                          Column('name_claim_4', String(256), nullable=True),
                          Column('score_claim_4_min', SmallInteger, nullable=True),
                          Column('score_claim_4_max', SmallInteger, nullable=True),
                          Column('score_claim_4_weight', Float, nullable=True),
                          Column('asmt_claim_perf_lvl_name_1', String(256), nullable=True),
                          Column('asmt_claim_perf_lvl_name_2', String(256), nullable=True),
                          Column('asmt_claim_perf_lvl_name_3', String(256), nullable=True),
                          Column('name_perf_lvl_1', String(256), nullable=True),
                          Column('name_perf_lvl_2', String(256), nullable=True),
                          Column('name_perf_lvl_3', String(256), nullable=True),
                          Column('name_perf_lvl_4', String(256), nullable=True),
                          Column('name_perf_lvl_5', String(256), nullable=True),
                          Column('score_cut_point_1', SmallInteger, nullable=True),
                          Column('score_cut_point_2', SmallInteger, nullable=True),
                          Column('score_cut_point_3', SmallInteger, nullable=True),
                          Column('score_cut_point_4', SmallInteger, nullable=True),
                          Column('effective_date', String(8), nullable=True),
                          Column('created_date', TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()')),
                          )

    int_sbac_asmt_outcome = Table('INT_SBAC_ASMT_OUTCOME', metadata,
                                  Column('record_sid', BigInteger, primary_key=True),
                                  Column('op', String(1), server_default='C', nullable=False),
                                  Column('guid_batch', String(256), nullable=False),
                                  Column('guid_asmt', String(50), nullable=True),
                                  Column('guid_asmt_location', String(50), nullable=True),
                                  Column('name_asmt_location', String(256), nullable=True),
                                  Column('grade_asmt', String(10), nullable=False),
                                  Column('name_state', String(32), nullable=False),
                                  Column('code_state', String(2), nullable=False),
                                  Column('guid_district', String(50), nullable=False),
                                  Column('name_district', String(256), nullable=False),
                                  Column('guid_school', String(50), nullable=False),
                                  Column('name_school', String(256), nullable=False),
                                  Column('type_school', String(20), nullable=False),
                                  Column('guid_student', String(50), nullable=False),
                                  Column('external_student_id', String(256), nullable=True),
                                  Column('name_student_first', String(256), nullable=True),
                                  Column('name_student_middle', String(256), nullable=True),
                                  Column('name_student_last', String(256), nullable=True),
                                  Column('address_student_line1', String(256), nullable=True),
                                  Column('address_student_line2', String(256), nullable=True),
                                  Column('address_student_city', String(100), nullable=True),
                                  Column('address_student_zip', String(5), nullable=True),
                                  Column('gender_student', String(10), nullable=True),
                                  Column('email_student', String(256), nullable=True),
                                  Column('dob_student', String(8), nullable=True),
                                  Column('grade_enrolled', String(10), nullable=False),
                                  Column('dmg_eth_hsp', Boolean, nullable=True),
                                  Column('dmg_eth_ami', Boolean, nullable=True),
                                  Column('dmg_eth_asn', Boolean, nullable=True),
                                  Column('dmg_eth_blk', Boolean, nullable=True),
                                  Column('dmg_eth_pcf', Boolean, nullable=True),
                                  Column('dmg_eth_wht', Boolean, nullable=True),
                                  Column('dmg_prg_iep', Boolean, nullable=True),
                                  Column('dmg_prg_lep', Boolean, nullable=True),
                                  Column('dmg_prg_504', Boolean, nullable=True),
                                  Column('dmg_prg_tt1', Boolean, nullable=True),
                                  Column('dmg_eth_derived', SmallInteger, nullable=True),
                                  Column('date_assessed', String(8), nullable=False),
                                  Column('date_taken_day', SmallInteger, nullable=False),
                                  Column('date_taken_month', SmallInteger, nullable=False),
                                  Column('date_taken_year', SmallInteger, nullable=False),
                                  Column('score_asmt', SmallInteger, nullable=False),
                                  Column('score_asmt_min', SmallInteger, nullable=False),
                                  Column('score_asmt_max', SmallInteger, nullable=False),
                                  Column('score_perf_level', SmallInteger, nullable=False),
                                  Column('score_claim_1', SmallInteger, nullable=True),
                                  Column('score_claim_1_min', SmallInteger, nullable=True),
                                  Column('score_claim_1_max', SmallInteger, nullable=True),
                                  Column('asmt_claim_1_perf_lvl', SmallInteger, nullable=True),
                                  Column('score_claim_2', SmallInteger, nullable=True),
                                  Column('score_claim_2_min', SmallInteger, nullable=True),
                                  Column('score_claim_2_max', SmallInteger, nullable=True),
                                  Column('asmt_claim_2_perf_lvl', SmallInteger, nullable=True),
                                  Column('score_claim_3', SmallInteger, nullable=True),
                                  Column('score_claim_3_min', SmallInteger, nullable=True),
                                  Column('score_claim_3_max', SmallInteger, nullable=True),
                                  Column('asmt_claim_3_perf_lvl', SmallInteger, nullable=True),
                                  Column('score_claim_4', SmallInteger, nullable=True),
                                  Column('score_claim_4_min', SmallInteger, nullable=True),
                                  Column('score_claim_4_max', SmallInteger, nullable=True),
                                  Column('asmt_claim_4_perf_lvl', SmallInteger, nullable=True),
                                  Column('asmt_type', String(16), nullable=False),
                                  Column('asmt_subject', String(32), nullable=False),
                                  Column('asmt_year', SmallInteger, nullable=False),
                                  Column('created_date', TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()')),
                                  Column('acc_asl_video_embed', SmallInteger, nullable=False),
                                  Column('acc_asl_human_nonembed', SmallInteger, nullable=False),
                                  Column('acc_braile_embed', SmallInteger, nullable=False),
                                  Column('acc_closed_captioning_embed', SmallInteger, nullable=False),
                                  Column('acc_text_to_speech_embed', SmallInteger, nullable=False),
                                  Column('acc_abacus_nonembed', SmallInteger, nullable=False),
                                  Column('acc_alternate_response_options_nonembed', SmallInteger, nullable=False),
                                  Column('acc_calculator_nonembed', SmallInteger, nullable=False),
                                  Column('acc_multiplication_table_nonembed', SmallInteger, nullable=False),
                                  Column('acc_print_on_demand_nonembed', SmallInteger, nullable=False),
                                  Column('acc_read_aloud_nonembed', SmallInteger, nullable=False),
                                  Column('acc_scribe_nonembed', SmallInteger, nullable=False),
                                  Column('acc_speech_to_text_nonembed', SmallInteger, nullable=False),
                                  Column('acc_streamline_mode', SmallInteger, nullable=False),
                                  )

    int_sbac_stu_reg = Table('INT_SBAC_STU_REG', metadata,
                             Column('record_sid', BigInteger, primary_key=True),
                             Column('guid_batch', String(36), nullable=False),
                             Column('name_state', String(50), nullable=False),
                             Column('code_state', String(2), nullable=False),
                             Column('guid_district', String(30), nullable=False),
                             Column('name_district', String(60), nullable=False),
                             Column('guid_school', String(30), nullable=False),
                             Column('name_school', String(60), nullable=False),
                             Column('guid_student', String(30), nullable=False),
                             Column('external_ssid_student', String(50), nullable=False),
                             Column('name_student_first', String(35), nullable=True,),
                             Column('name_student_middle', String(35), nullable=True,),
                             Column('name_student_last', String(35), nullable=True,),
                             Column('gender_student', String(6), nullable=False),
                             Column('dob_student', String(10), nullable=True,),
                             Column('grade_enrolled', String(2), nullable=False),
                             Column('dmg_eth_hsp', Boolean, nullable=False),
                             Column('dmg_eth_ami', Boolean, nullable=False),
                             Column('dmg_eth_asn', Boolean, nullable=False),
                             Column('dmg_eth_blk', Boolean, nullable=False),
                             Column('dmg_eth_pcf', Boolean, nullable=False),
                             Column('dmg_eth_wht', Boolean, nullable=False),
                             Column('dmg_prg_iep', Boolean, nullable=False),
                             Column('dmg_prg_lep', Boolean, nullable=False),
                             Column('dmg_prg_504', Boolean, nullable=True,),
                             Column('dmg_sts_ecd', Boolean, nullable=False),
                             Column('dmg_sts_mig', Boolean, nullable=True,),
                             Column('dmg_multi_race', Boolean, nullable=False),
                             Column('code_confirm', String(35), nullable=False),
                             Column('code_language', String(3), nullable=True,),
                             Column('eng_prof_lvl', String(20), nullable=True,),
                             Column('us_school_entry_date', String(10), nullable=True,),
                             Column('lep_entry_date', String(10), nullable=True,),
                             Column('lep_exit_date', String(10), nullable=True,),
                             Column('t3_program_type', String(27), nullable=True,),
                             Column('prim_disability_type', String(3), nullable=True,),
                             Column('created_date', TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()')),
                             )

    int_sbac_stu_reg_meta = Table('INT_SBAC_STU_REG_META', metadata,
                                  Column('record_sid', BigInteger, primary_key=True),
                                  Column('guid_batch', String(36), nullable=False),
                                  Column('guid_registration', String(50), nullable=False),
                                  Column('academic_year', SmallInteger, nullable=False),
                                  Column('extract_date', String(10), nullable=False),
                                  Column('test_reg_id', String(50), nullable=False),
                                  Column('created_date', TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()')),
                                  )

    ref_column_mapping = Table('REF_COLUMN_MAPPING', metadata,
                               Column('column_map_key', BigInteger, primary_key=True),
                               Column('phase', SmallInteger, nullable=True),
                               Column('source_table', String(50), nullable=False),
                               Column('source_column', String(256), nullable=True),
                               Column('target_table', String(50), nullable=True),
                               Column('target_column', String(50), nullable=True),
                               Column('transformation_rule', String(50), nullable=True),
                               Column('stored_proc_name', String(256), nullable=True),
                               Column('stored_proc_created_date', TIMESTAMP(timezone=True), nullable=True),
                               Column('created_date', TIMESTAMP(timezone=True), server_default=text('NOW()'), nullable=False),
                               )

    sr_ref_column_mapping = Table('SR_REF_COLUMN_MAPPING', metadata,
                                  Column('column_map_key', BigInteger, primary_key=True),
                                  Column('phase', SmallInteger, nullable=True),
                                  Column('source_table', String(50), nullable=False),
                                  Column('source_column', String(256), nullable=True),
                                  Column('target_table', String(50), nullable=True),
                                  Column('target_column', String(50), nullable=True),
                                  Column('transformation_rule', String(50), nullable=True),
                                  Column('stored_proc_name', String(256), nullable=True),
                                  Column('stored_proc_created_date', TIMESTAMP(timezone=True), nullable=True),
                                  Column('created_date', TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()')),
                                  )

    master_metadata = Table('MASTER_METADATA', metadata,
                            Column('metadata_sid', BigInteger, primary_key=True),
                            Column('tenant_code', String(10), nullable=False),
                            Column('tenant_name', String(255), nullable=True),
                            Column('udl_tenant_schema', String(255), nullable=True),
                            Column('target_db_host', String(255), nullable=False),
                            Column('target_db_name', String(255), nullable=False),
                            Column('target_schema_name', String(255), nullable=False),
                            Column('target_schema_port', SmallInteger, nullable=False),
                            Column('target_schema_user_name', String(255), nullable=False),
                            Column('target_schema_passwd', String(255), nullable=False),
                            Column('created_date', TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()')),
                            )

    return metadata


def generate_udl2_sequences(schema_name=None, metadata=None):
    '''
    generate_udl2_sequences returns all udl2 related sequences as a tuple.
    '''
    seq1 = Sequence(name='GLOBAL_REC_SEQ', start=1, increment=1, schema=schema_name,
                    optional=True, quote='Global record id sequences. form 1 to 2^63 -1 on postgresql', metadata=metadata)
    return (seq1, )
