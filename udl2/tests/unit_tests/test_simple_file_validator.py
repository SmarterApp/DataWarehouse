from sfv import simple_file_validator
from sfv import csv_validator
from sfv import json_validator
from sfv import error_codes
from sfv import config
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
        test_csv_fields = config.CSV_FIELD_MAPPINGS
        validator = csv_validator.DoesSourceFileInExpectedFormat(csv_fields=test_csv_fields)
        results = [validator.execute(self.conf['zones']['datafiles'],
                                     'test_data_valid_latest_11122013/'
                                     'REALDATA_ASMT_ID_4e1c189b-782c-4b9f-a0a7-cd521bff1f62.csv', 1)]
        assert len(results) == 1
        assert results[0][0] == '0'
