from rule_maker.rules import validations as v
BY_COLUMN = 'by_column'
BY_RULE = 'by_row'

# UDL config file using our notation system

validations = {
    'STG_SBAC_ASMT_OUTCOME': {
        BY_COLUMN: {
            'batch_id':[],
            'src_file_rec_num':[],
            'guid_asmt':[],
            'guid_asmt_location':[IsGoodGuid, {IsUniqueWithin: ['name_asmt_location']}],
            'name_asmt_location': IsNotNull,
            'grade_asmt':[IsNotNull, {InList:[3,4,5,6,7,8,11]}],
            'name_state':[],
            'code_state':[],
            'guid_district':[],
            'name_district':[],
            'guid_school':[],
            'name_school':[],
            'type_school':[],
            'guid_student':[],
            'name_student_first':[],
            'name_student_middle':[],
            'name_student_last':[],
            'address_student_line1':[],
            'address_student_line2':[],
            'address_student_city':[],
            'address_student_zip':[],
            'gender_student':[],
            'email_student':[],
            'dob_student':[],
            'grade_enrolled':[],
            'date_assessed':[],
            'score_asmt':[],
            'score_asmt_min':[],
            'score_asmt_max':[],
            'score_perf_level':[],
            'score_claim_1':[],
            'score_claim_1_min':[],
            'score_claim_1_max':[],
            'score_claim_2':[],
            'score_claim_2_min':[],
            'score_claim_2_max':[],
            'score_claim_3':[],
            'score_claim_3_min':[],
            'score_claim_3_max':[],
            'score_claim_4':[],
            'score_claim_4_min':[],
            'score_claim_4_max':[],
            'guid_staff':[],
            'name_staff_first':[],
            'name_staff_middle':[],
            'name_staff_last':[],
            'type_staff':[],
            'created_date':[]
        },
        BY_RULE: {

        }
    },
    'STG_SBAC_ASMT': {
        BY_COLUMN: {
              'record_sid':[],
              'batch_id':[],
              'guid_asmt':[],
              'type':[],
              'period':[],
              'year':[],
              'version':[],
              'subject':[],
              'score_overall_min':[],
              'score_overall_max':[],
              'name_claim_1':[],
              'score_claim_1_min':[],
              'score_claim_1_max':[],
              'score_claim_1_weight':[],
              'name_claim_2':[],
              'score_claim_2_min':[],
              'score_claim_2_max':[],
              'score_claim_2_weight':[],
              'name_claim_3':[],
              'score_claim_3_min':[],
              'score_claim_3_max':[],
              'score_claim_3_weight':[],
              'name_claim_4':[],
              'score_claim_4_min':[],
              'score_claim_4_max':[],
              'score_claim_4_weight':[],
              'name_perf_lvl_1':[],
              'name_perf_lvl_2':[],
              'name_perf_lvl_3':[],
              'name_perf_lvl_4':[],
              'name_perf_lvl_5':[],
              'score_cut_point_1':[],
              'score_cut_point_2':[],
              'score_cut_point_3':[],
              'score_cut_point_4':[],
              'created_date':[]
        },
        BY_ROW: {

        }
    }
}
