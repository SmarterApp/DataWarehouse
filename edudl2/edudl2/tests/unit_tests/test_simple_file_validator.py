from edudl2.sfv import simple_file_validator
from edudl2.sfv import csv_validator
from edudl2.exceptions.errorcodes import ErrorCode
import unittest
from edudl2.udl2.defaults import UDL2_DEFAULT_CONFIG_PATH_FILE
import os
from edudl2.udl2_util.config_reader import read_ini_file
from edudl2.database.udl2_connector import initialize_all_db
from edudl2.udl2.celery import udl2_conf, udl2_flat_conf


class UnitTestSimpleFileValidator(unittest.TestCase):

    def setUp(self, ):
        try:
            config_path = dict(os.environ)['UDL2_CONF']
        except Exception:
            config_path = UDL2_DEFAULT_CONFIG_PATH_FILE
        conf_tup = read_ini_file(config_path)
        self.conf = conf_tup[0]
        initialize_all_db(udl2_conf, udl2_flat_conf)
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

    def test_simple_file_validator_passes_for_valid_assmt_csv(self):
        validator = simple_file_validator.SimpleFileValidator('assessment')
        results = validator.execute(self.data_dir,
                                    'test_data_latest/'
                                    'REALDATA_ASMT_ID_f1451acb-72fc-43e4-b459-3227d52a5da0.csv', 1)
        self.assertEqual(len(results), 1)

    def test_simple_file_validator_passes_for_valid_student_reg_csv(self):
        validator = simple_file_validator.SimpleFileValidator('studentregistration')
        results = validator.execute(self.data_dir, 'student_registration_data/test_sample_student_reg.csv', 1)
        self.assertEqual(len(results), 1)

    def test_simple_file_validator_fails_for_missing_csv(self):
        validator = simple_file_validator.SimpleFileValidator('assessment')
        results = validator.execute(self.data_dir, 'nonexistent.csv', 1)
        self.assertEqual(results[0][0], ErrorCode.SRC_FILE_NOT_ACCESSIBLE_SFV, "Wrong error code")
        validator = simple_file_validator.SimpleFileValidator('studentregistration')
        results = validator.execute(self.data_dir, 'nonexistent.csv', 1)
        self.assertEqual(results[0][0], ErrorCode.SRC_FILE_NOT_ACCESSIBLE_SFV, "Wrong error code")

    def test_simple_file_validator_invalid_extension(self):
        validator = simple_file_validator.SimpleFileValidator('assessment')
        results = validator.execute(self.data_dir, 'invalid_ext.xls', 1)
        self.assertEqual(results[0][0], ErrorCode.SRC_FILE_TYPE_NOT_SUPPORTED)
        validator = simple_file_validator.SimpleFileValidator('studentregistration')
        results = validator.execute(self.data_dir, 'invalid_ext.xls', 1)
        self.assertEqual(results[0][0], ErrorCode.SRC_FILE_TYPE_NOT_SUPPORTED)

    def test_for_source_file_with_less_number_of_columns(self):
        test_csv_fields = {'guid_batch', 'student_guid'}
        validator = csv_validator.DoesSourceFileInExpectedFormat('assessment', csv_fields=test_csv_fields)
        error_code_expected = ErrorCode.SRC_FILE_HAS_HEADERS_MISMATCH_EXPECTED_FORMAT
        results = [validator.execute(self.data_dir,
                                     'invalid_csv.csv', 1)]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], error_code_expected)

    def test_for_source_file_with_mismatched_format(self):
        test_csv_fields = {'guid_batch', 'student_guid'}
        validator = csv_validator.DoesSourceFileInExpectedFormat('studentregistration', csv_fields=test_csv_fields)
        error_code_expected = ErrorCode.SRC_FILE_HAS_HEADERS_MISMATCH_EXPECTED_FORMAT
        results = [validator.execute(self.data_dir,
                                     'invalid_csv.csv', 1)]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], error_code_expected)

    def test_simple_file_validator_wrong_delimiter(self):
        validator = simple_file_validator.SimpleFileValidator('assessment')
        results = validator.execute(self.data_dir, 'REALDATA_3005.csv', 1)
        self.assertEqual(results[1][0], ErrorCode.SRC_FILE_WRONG_DELIMITER)

    def test_for_source_file_with_matching_columns(self):
        test_csv_fields = ['AssessmentAdministrationFinishDate', 'Birthdate',
                           'AssessmentLevelForWhichDesigned', 'GradeLevelWhenAssessed', 'Group1Id', 'Group1Text', 'Group2Id', 'Group2Text',
                           'AssessmentGuid', 'AssessmentSessionLocationId', 'ResponsibleDistrictIdentifier', 'ResponsibleSchoolIdentifier',
                           'StudentIdentifier', 'ExternalSSID', 'StateAbbreviation',
                           'AssessmentSessionLocation', 'OrganizationName', 'NameOfInstitution', 'FirstName',
                           'LastOrSurname', 'MiddleName', 'AssessmentSubtestResultScoreValue', 'AssessmentSubtestMaximumValue', 'AssessmentSubtestMinimumValue',
                           'AssessmentSubtestResultScoreClaim1Value', 'AssessmentSubtestClaim1MaximumValue', 'AssessmentSubtestClaim1MinimumValue',
                           'AssessmentClaim1PerformanceLevelIdentifier', 'AssessmentSubtestResultScoreClaim2Value',
                           'AssessmentSubtestClaim2MaximumValue', 'AssessmentSubtestClaim2MinimumValue', 'AssessmentClaim2PerformanceLevelIdentifier', 'AssessmentSubtestResultScoreClaim3Value',
                           'AssessmentSubtestClaim3MaximumValue', 'AssessmentSubtestClaim3MinimumValue', 'AssessmentClaim3PerformanceLevelIdentifier',
                           'AssessmentSubtestResultScoreClaim4Value', 'AssessmentSubtestClaim4MaximumValue',
                           'AssessmentSubtestClaim4MinimumValue', 'AssessmentClaim4PerformanceLevelIdentifier', 'AssessmentPerformanceLevelIdentifier', 'AssessmentYear', 'Sex',
                           'HispanicOrLatinoEthnicity', 'AmericanIndianOrAlaskaNative', 'Asian', 'BlackOrAfricanAmerican', 'NativeHawaiianOrOtherPacificIslander',
                           'White', 'DemographicRaceTwoOrMoreRaces', 'IDEAIndicator', 'LEPStatus', 'Section504Status', 'EconomicDisadvantageStatus', 'MigrantStatus',
                           'AssessmentAcademicSubject', 'AssessmentType', 'AccommodationAmericanSignLanguage', 'AccommodationSignLanguageHumanIntervention',
                           'AccommodationBraille', 'AccommodationClosedCaptioning', 'AccommodationTextToSpeech', 'AccommodationAbacus',
                           'AccommodationAlternateResponseOptions', 'AccommodationCalculator', 'AccommodationMultiplicationTable',
                           'AccommodationPrintOnDemand', 'AccommodationReadAloud', 'AccommodationScribe', 'AccommodationSpeechToText',
                           'AccommodationStreamlineMode']
        validator = csv_validator.DoesSourceFileInExpectedFormat('assessment', csv_fields=test_csv_fields)
        results = [validator.execute(self.data_dir,
                                     'test_data_latest/'
                                     'REALDATA_ASMT_ID_f1451acb-72fc-43e4-b459-3227d52a5da0.csv', 1)]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], '0')

    def test_valid_student_registration_json(self):
        validator = simple_file_validator.SimpleFileValidator('studentregistration')
        results = validator.execute(self.data_dir,
                                    'student_registration_data/test_sample_student_reg.json', 1)
        self.assertEqual(len(results), 0)

    def test_invalid_content_student_registration_json(self):
        validator = simple_file_validator.SimpleFileValidator('studentregistration')
        results = validator.execute(self.data_dir,
                                    'student_registration_data/test_invalid_student_reg.json', 1)
        error_code_expected = ErrorCode.SRC_JSON_INVALID_FORMAT
        expected_field = 'academic_year'
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], error_code_expected)
        self.assertEqual(results[0][4], expected_field)
