import json
import os
from sfv import error_codes


class JsonValidator():
    """
    Invoke a suite of validations for json files.
    """

    def __init__(self):
        self.validators = [IsValidJsonFile(),
                           HasExpectedFormat()]

    def execute(self, dir_path, file_name, batch_sid):
        """
        Run all validation tests and return a list of error codes for all failures, or
        errorcodes.STATUS_OK if all tests pass

        @param dir_path: path of the file
        @type dir_path: string
        @param file_name: name of the file
        @type file_name: string
        @param batch_sid: batch id of the file
        @type batch_sid: integer
        @return: tuple of the form: (status_code, dir_path, file_name, batch_sid)
        """
        error_list = []
        for validator in self.validators:
            result = validator.execute(dir_path, file_name, batch_sid)
            if result[0] != error_codes.STATUS_OK:
                error_list.append(result)
            else:
                pass
        return error_list


class IsValidJsonFile(object):
    '''Make sure the file contains a parsable json string'''

    def execute(self, dir_path, file_name, batch_sid):
        '''
        Run json.load() on the given file, if it is invalid json, the exception will be caught and the proper code returned

        @param dir_path: path of the file
        @type dir_path: string
        @param file_name: name of the file
        @type file_name: string
        @param batch_sid: batch id of the file
        @type batch_sid: integer
        @return: tuple of the form: (status_code, dir_path, file_name, batch_sid)
        '''
        complete_path = os.path.join(dir_path, file_name)
        with open(complete_path) as f:
            try:
                json_object = json.load(f)
                return (error_codes.STATUS_OK, dir_path, file_name, batch_sid)
            except ValueError as e:
                return (error_codes.SRC_JSON_INVALID_STRUCTURE, dir_path, file_name, batch_sid)


class HasExpectedFormat(object):
    '''Make sure the JSON file is formatted to our standards '''
    def __init__(self):

        # mapping is a dictionary with keys = fields and values = paths to that field within the json structure
        # the paths will consist of a list of strings, each one a component of the path to the given field
        self.mapping = {'asmt_guid': ['identification', 'guid'],
                        'asmt_type': ['identification', 'type'],
                        'asmt_period': ['identification', 'period'],
                        'asmt_period_year': ['identification', 'year'],
                        'asmt_version': ['identification', 'version'],
                        'asmt_subject': ['identification', 'subject'],
                        'asmt_claim_1_name': ['claims', 'claim_1', 'name'],
                        'asmt_claim_2_name': ['claims', 'claim_2', 'name'],
                        'asmt_claim_3_name': ['claims', 'claim_3', 'name'],
                        'asmt_claim_4_name': ['claims', 'claim_4', 'name'],
                        'asmt_perf_lvl_name_1': ['performance_levels', 'level_1', 'name'],
                        'asmt_perf_lvl_name_2': ['performance_levels', 'level_2', 'name'],
                        'asmt_perf_lvl_name_3': ['performance_levels', 'level_3', 'name'],
                        'asmt_perf_lvl_name_4': ['performance_levels', 'level_4', 'name'],
                        'asmt_perf_lvl_name_5': ['performance_levels', 'level_5', 'name'],
                        'asmt_score_min': ['overall', 'min_score'],
                        'asmt_score_max': ['overall', 'max_score'],
                        'asmt_claim_1_score_min': ['claims', 'claim_1', 'min_score'],
                        'asmt_claim_1_score_max': ['claims', 'claim_1', 'max_score'],
                        'asmt_claim_1_score_weight': ['claims', 'claim_1', 'weight'],
                        'asmt_claim_2_score_min': ['claims', 'claim_2', 'min_score'],
                        'asmt_claim_2_score_max': ['claims', 'claim_2', 'max_score'],
                        'asmt_claim_2_score_weight': ['claims', 'claim_2', 'weight'],
                        'asmt_claim_3_score_min': ['claims', 'claim_3', 'min_score'],
                        'asmt_claim_3_score_max': ['claims', 'claim_3', 'max_score'],
                        'asmt_claim_3_score_weight': ['claims', 'claim_3', 'weight'],
                        'asmt_claim_4_score_min': ['claims', 'claim_4', 'min_score'],
                        'asmt_claim_4_score_max': ['claims', 'claim_4', 'max_score'],
                        'asmt_claim_4_score_weight': ['claims', 'claim_4', 'weight'],
                        'asmt_cut_point_1': ['performance_levels', 'level_2', 'cut_point'],
                        'asmt_cut_point_2': ['performance_levels', 'level_3', 'cut_point'],
                        'asmt_cut_point_3': ['performance_levels', 'level_4', 'cut_point'],
                        'asmt_cut_point_4': ['performance_levels', 'level_5', 'cut_point']
                        }

    def execute(self, dir_path, file_name, batch_sid):
        '''
        Iterate through all the elements of mapping, and check that we can reach all expected fields using
        the provided paths.

        @param dir_path: path of the file
        @type dir_path: string
        @param file_name: name of the file
        @type file_name: string
        @param batch_sid: batch id of the file
        @type batch_sid: integer
        @return: tuple of the form: (status_code, dir_path, file_name, batch_sid, field) or (status_code, dir_path, file_name, batch_sid)
        '''

        complete_path = os.path.join(dir_path, file_name)
        with open(complete_path) as f:
            json_object = json.load(f)
            mapping = self.mapping
            for field in mapping.keys():
                path = mapping[field]
                if not self.does_json_path_exist(json_object, path):
                    return (error_codes.SRC_JSON_INVALID_FORMAT, dir_path, file_name, batch_sid, field)
            return (error_codes.STATUS_OK, dir_path, file_name, batch_sid)

    def does_json_path_exist(self, json_object, path):
        '''
        Given a json_object [a dictionary] and a path [a list of keys through the dictionary], ensure we can follow the path
        all the way through the json_object

        @param json_object: A dictionary that represents some json object
        @type json_object: dict
        @param path: A list of components that form a path through the json_object
        @type path: list of str
        @return: whether or not the given path exists within json_object
        @rtype: bool
        '''
        current_position = json_object
        for component in path:
            if component in current_position.keys():
                current_position = current_position[component]
            else:
                return False
        return True
