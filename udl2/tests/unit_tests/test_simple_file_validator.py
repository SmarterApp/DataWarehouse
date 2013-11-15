from sfv import simple_file_validator
from sfv import csv_validator
from sfv import error_codes
import unittest
from udl2.defaults import UDL2_DEFAULT_CONFIG_PATH_FILE
import imp


class UnitTestSimpleFileValidator(unittest.TestCase):

    def setUp(self, ):
        try:
            config_path = dict(os.environ)['UDL2_CONF']
        except Exception:
            config_path = UDL2_DEFAULT_CONFIG_PATH_FILE
        udl2_conf = imp.load_source('udl2_conf', config_path)
        from udl2_conf import udl2_conf
        self.conf = udl2_conf

    def test_simple_file_validator_passes_for_valid_csv(self):
        validator = simple_file_validator.SimpleFileValidator()
        results = validator.execute(self.conf['zones']['datafiles'],
                                    'test_data_valid_latest_11122013/'
                                    'REALDATA_ASMT_ID_4e1c189b-782c-4b9f-a0a7-cd521bff1f62.csv', 1)
        assert len(results) == 0

    def test_simple_file_validator_fails_for_missing_csv(self):
        validator = simple_file_validator.SimpleFileValidator()
        results = validator.execute(self.conf['zones']['datafiles'], 'nonexistent.csv', 1)
        assert results[0][0] == error_codes.SRC_FILE_NOT_ACCESSIBLE_SFV, "Wrong error code"

    def test_simple_file_validator_invalid_extension(self):
        validator = simple_file_validator.SimpleFileValidator()
        results = validator.execute(self.conf['zones']['datafiles'], 'invalid_ext.xls', 1)
        assert results[0][0] == error_codes.SRC_FILE_TYPE_NOT_SUPPORTED

    def test_for_source_file_with_less_number_of_columns(self):
        test_csv_fields = {'guid_batch', 'student_guid'}
        validator = csv_validator.DoesSourceFileInExpectedFormat(csv_fields=test_csv_fields)
        error_code_expected = error_codes.SRC_FILE_HAS_HEADERS_MISMATCH_EXPECTED_FORMAT
        results = [validator.execute(self.conf['zones']['datafiles'],
                                     'invalid_csv.csv', 1)]
        assert len(results) == 1
        assert results[0][0] == error_code_expected

    def test_for_source_file_with_matching_columns(self):
        test_csv_fields = ['date_assessed', 'dob_student', 'type_school', 'address_student_city', 'address_student_line1', 'address_student_line2', 'address_student_zip',
                           'email_student', 'grade_asmt', 'grade_enrolled', 'guid_asmt', 'guid_asmt_location', 'guid_district', 'guid_school', 'guid_staff', 'guid_student',
                           'name_asmt_location', 'name_district', 'name_school', 'name_staff_first', 'name_staff_last', 'name_staff_middle', 'name_state', 'name_student_first',
                           'name_student_last', 'name_student_middle', 'score_asmt', 'score_asmt_max', 'score_asmt_min', 'score_claim_1', 'score_claim_1_max', 'score_claim_1_min',
                           'score_claim_2', 'score_claim_2_max', 'score_claim_2_min', 'score_claim_3', 'score_claim_3_max', 'score_claim_3_min', 'score_claim_4', 'score_claim_4_max',
                           'score_claim_4_min', 'score_perf_level', 'asmt_year', 'gender_student', 'dmg_eth_hsp', 'dmg_eth_ami', 'dmg_eth_asn', 'dmg_eth_blk', 'dmg_eth_pcf',
                           'dmg_eth_wht', 'dmg_prg_iep', 'dmg_prg_lep', 'dmg_prg_504', 'dmg_prg_tt1', 'code_state', 'asmt_subject', 'asmt_type', 'type_staff']
        validator = csv_validator.DoesSourceFileInExpectedFormat(csv_fields=test_csv_fields)
        results = [validator.execute(self.conf['zones']['datafiles'],
                                     'test_data_valid_latest_11122013/'
                                     'REALDATA_ASMT_ID_4e1c189b-782c-4b9f-a0a7-cd521bff1f62.csv', 1)]
        assert len(results) == 1
        assert results[0][0] == '0'
