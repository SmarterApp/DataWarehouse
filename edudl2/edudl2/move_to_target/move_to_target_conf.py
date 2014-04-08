__author__ = 'swimberly'


def get_move_to_target_conf():
    """
    configurations for move_to_target to match tables for foreign key rec ids for dim_asmt, dim_student,
    and dim_inst_hier. It also containts matcher configuration for UDL delete/update against production tables.
    :return:
    """

    conf = {
        'asmt_rec_id': {
            'rec_id': 'asmt_rec_id',
            'target_table': 'dim_asmt',
            'source_table': 'int_sbac_asmt',
            'guid_column_name': 'asmt_guid',
            'guid_column_in_source': 'guid_asmt'
        },
        'section_rec_id_info': {
            'rec_id': 'section_rec_id',
            'value': '1'
        },
        'handle_deletions': {
            'prod_table': 'fact_asmt_outcome',
            'target_table': 'fact_asmt_outcome',
            'find_deleted_fact_asmt_outcome_rows': {'columns': ['asmnt_outcome_rec_id', 'student_guid', 'asmt_guid', 'date_taken', 'rec_status'],
                                                    'condition': ['rec_status'],
                                                    'rec_status': 'W'},
            'match_delete_fact_asmt_outcome_row_in_prod': {'columns': ['asmnt_outcome_rec_id', 'student_guid',
                                                                       'asmt_guid', 'date_taken'],
                                                           'condition': ['student_guid', 'asmt_guid', 'date_taken', 'rec_status'],
                                                           'rec_status': 'C'},
            'update_matched_fact_asmt_outcome_row': {'columns': {'asmnt_outcome_rec_id': 'asmnt_outcome_rec_id',
                                                                 'rec_status': 'new_status'},
                                                     'new_status': 'D',
                                                     'condition': ['student_guid', 'asmt_guid', 'date_taken', 'rec_status'],
                                                     'rec_status': 'W'},
        }
    }

    return conf
