__author__ = 'sravi'


class Constants():
    """
    constants related to udl db schema
    """
    # table names
    SR_TARGET_TABLE = 'student_reg'

    # staging tables
    STG_ASMT_OUT_TABLE = 'stg_sbac_asmt_outcome'
    STG_SR_TABLE = 'stg_sbac_stu_reg'

    # integration tables
    INT_ASMT_TABLE = 'int_sbac_asmt'
    INT_ASMT_OUT_TABLE = 'int_sbac_asmt_outcome'
    INT_SR_META_TABLE = 'int_sbac_stu_reg_meta'
    INT_SR_TABLE = 'int_sbac_stu_reg'

    # other tables
    UDL2_BATCH_TABLE = 'udl_batch'
    ASMT_REF_TABLE = 'ref_column_mapping'
    SR_REF_TABLE = 'sr_ref_column_mapping'
    UDL2_ERR_LIST_TABLE = 'err_list'
    UDL2_CSV_LZ_TABLE = 'lz_csv'
    UDL2_JSON_LZ_TABLE = 'lz_json'
    UDL2_FDW_SERVER = 'udl2_fdw_server'

    # column values
    OP_COLUMN_NAME = 'op'

    # load types
    LOAD_TYPE_KEY = 'content'
    LOAD_TYPE_ASSESSMENT = 'assessment'
    LOAD_TYPE_STUDENT_REGISTRATION = 'studentregistration'

    # global sequence name
    SEQUENCE_NAME = 'global_rec_seq'

    # Phase number
    INT_TO_STAR_PHASE = 4

    # lambdas for returning list of constants or constants based on some condition
    # TODO: in future this will be replaced with dynamic udl schema based on load being processed
    LOAD_TYPES = lambda: [Constants.LOAD_TYPE_ASSESSMENT, Constants.LOAD_TYPE_STUDENT_REGISTRATION]
    UDL2_STAGING_TABLE = lambda load_type: {Constants.LOAD_TYPE_ASSESSMENT:
                                            Constants.STG_ASMT_OUT_TABLE,
                                            Constants.LOAD_TYPE_STUDENT_REGISTRATION:
                                            Constants.STG_SR_TABLE}.get(load_type, None)
    UDL2_INTEGRATION_TABLE = lambda load_type: {Constants.LOAD_TYPE_ASSESSMENT:
                                                Constants.INT_ASMT_OUT_TABLE,
                                                Constants.LOAD_TYPE_STUDENT_REGISTRATION:
                                                Constants.INT_SR_TABLE}.get(load_type, None)
    UDL2_JSON_INTEGRATION_TABLE = lambda load_type: {Constants.LOAD_TYPE_ASSESSMENT:
                                                     Constants.INT_ASMT_TABLE,
                                                     Constants.LOAD_TYPE_STUDENT_REGISTRATION:
                                                     Constants.INT_SR_META_TABLE}.get(load_type, None)
    UDL2_REF_MAPPING_TABLE = lambda load_type: {Constants.LOAD_TYPE_ASSESSMENT:
                                                Constants.ASMT_REF_TABLE,
                                                Constants.LOAD_TYPE_STUDENT_REGISTRATION:
                                                Constants.SR_REF_TABLE}.get(load_type, None)
