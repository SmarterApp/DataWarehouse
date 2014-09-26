import os
from edudl2.exceptions.errorcodes import ErrorCode
from edudl2.sfv import simple_file_validator
from edudl2.sfv import csv_validator
from edudl2.sfv import json_validator
from edudl2.tests.functional_tests import UDLFunctionalTestCase


class DataValidationErrorCode(UDLFunctionalTestCase):

    # For bad CSVFiles
    def test_sourcefolder_errorcode(self):
        CSV_FOLDER = "csv_file11"
        # Test # 1 -- > Check folder does exists or not (True / False), if not return Error 3001.
        csv_folder = os.path.join(self.data_dir, CSV_FOLDER)
        validate_instance = csv_validator.IsSourceFolderAccessible()
        expected_error_code = validate_instance.execute(csv_folder, CSV_FOLDER, 123)
        self.assertEqual(expected_error_code[0], ErrorCode.SRC_FOLDER_NOT_ACCESSIBLE_SFV, "Validation Code for CSV Source folder not accessible is incorrect")

    def test_sourcefile_errorcode(self):
        #  test#2 --> source_file_accessible
        validate_instance = csv_validator.IsSourceFileAccessible()
        expected_error_code = validate_instance.execute(self.data_dir, "REALDATA_3002.csv", 123)
        self.assertEqual(expected_error_code[0], ErrorCode.SRC_FILE_NOT_ACCESSIBLE_SFV, "Validation Code for CSV Source file not accessible is incorrect")

    def test_blankfile_errorcode(self):
        # test#3 --> blank_file
        validate_instance = csv_validator.IsFileBlank()
        expected_error_code = validate_instance.execute(self.data_dir, "realdata_3003.csv", 123)
        self.assertEqual(expected_error_code[0], ErrorCode.SRC_FILE_HAS_NO_DATA, "Validation Code for CSV blank file is incorrect")

    def test_wrong_delimiter_errorcode(self):
        # test#3 --> blank_file
        validate_instance = csv_validator.IsSourceFileCommaDelimited()
        expected_error_code = validate_instance.execute(self.data_dir, "REALDATA_3005.csv", 123)
        self.assertEqual(expected_error_code[0], ErrorCode.SRC_FILE_WRONG_DELIMITER, "Validation Code for CSV file with wrong delimiter is incorrect")

    def test_noHeader_errorcode(self):
        # test#4 --> no headers (3009)
        validate_instance = csv_validator.DoesSourceFileContainHeaders()
        expected_error_code = validate_instance.execute(self.data_dir, "realdata_3009.csv", 123)
        self.assertEqual(expected_error_code[0], ErrorCode.SRC_FILE_HAS_NO_HEADERS, "Validation Code for no header is incorrect")

    def test_duplicateHeaders_errorcode(self):
        # test#5 --> duplicate_values (3011)
        validate_instance = csv_validator.DoesSourceFileContainDuplicateHeaders()
        expected_error_code = validate_instance.execute(self.data_dir, "REALDATA_3011.csv", 123)
        self.assertEqual(expected_error_code[0], ErrorCode.SRC_FILE_HAS_DUPLICATE_HEADERS, "Validation Code for duplicate headers is incorrect")

    def test_noDataRow_errorcode(self):
        # test#6 --> DoesSourceFileHaveData
        validate_instance = csv_validator.DoesSourceFileHaveData()
        expected_error_code = validate_instance.execute(self.data_dir, "test_file_headers.csv", 123)
        self.assertEqual(expected_error_code[0], ErrorCode.SRC_FILE_HAS_NO_DATA, "Validation Code for atleast one data row is incorrect")

    def test_dataMismatch_errorcode(self):
        # test#7 --> dataFormate
        validate_instance = csv_validator.IsCsvWellFormed()
        expected_error_code = validate_instance.execute(self.data_dir, "REALDATA_3008.csv", 123)
        self.assertEqual(expected_error_code[0], ErrorCode.SRC_FILE_HEADERS_MISMATCH_DATA, "Validation Code for data mismatch row is incorrect")

    def test_extention_errorcode(self):
        #test#8 --> different file formate other than csv & json
        expected_error_code = simple_file_validator.SimpleFileValidator('assessment').execute(self.data_dir, "REALDATA_3010.xlsx", 123)
        self.assertEqual(expected_error_code[0][0], ErrorCode.SRC_FILE_TYPE_NOT_SUPPORTED, "Validation Code for different file formate is incorrect")

    # Test Cases for bad json file
    def test_jsonStructure_errorcode(self):
        #test# 9 --> file structure
        validate_instance = json_validator.JsonValidator('assessment').validators[0]
        expected_error_code = validate_instance.execute(self.data_dir, "METADATA_ASMT_3012.json", 123)
        self.assertEqual(expected_error_code[0], ErrorCode.SRC_JSON_INVALID_STRUCTURE, "Validation Code for JSON file structure is incorrect")

    def test_jsonFormate_errorcode(self):
        #Test#10 --> file formate
        validate_instance = json_validator.JsonValidator('assessment').validators[1]
        expected_error_code = validate_instance.execute(self.data_dir, "METADATA_ASMT_3013.json", 123)
        self.assertEqual(expected_error_code[0], ErrorCode.SRC_JSON_INVALID_FORMAT, "Validation Code for JSON file formate is incorrect")

    def test_multiple_errorcode(self):
        #test#11 --> test multiple errors in one csv file (Error: 3006, 3008 & 3011)
        multierror_list = [ErrorCode.SRC_FILE_HAS_DUPLICATE_HEADERS, ErrorCode.SRC_FILE_HEADERS_MISMATCH_DATA,
                           ErrorCode.SRC_FILE_HAS_HEADERS_MISMATCH_EXPECTED_FORMAT]
        errorcode_list = []
        expected_error_code = csv_validator.CsvValidator('assessment').execute(self.data_dir, "realdata_3008_3011.csv", 123)
        for i in range(len(expected_error_code)):
            errorcode_list.append(expected_error_code[i][0])
        self.assertEqual(len(multierror_list), len(errorcode_list))
        self.assertEqual(set(multierror_list), set(errorcode_list), "Error codes are incorrect for duplicate headers and for data mismatch")
