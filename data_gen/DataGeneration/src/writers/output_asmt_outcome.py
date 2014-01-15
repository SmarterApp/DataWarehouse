__author__ = 'swimberly'
import csv
import os
from datetime import date

from DataGeneration.src.utils.idgen import IdGen

CSV_K = 'csv'


def initialize_csv_file(output_config, output_keys, output_path):
    """
    Given the output configuration dictionary create the corresponding csv files
    :param output_config: A dictionary of configuration information
    :param output_keys: A list of output formats that should be initialized
        these strings must be the top level keys in the output config dictionary
    :return: a dictionary of output files
    """
    output_files = {}
    for out_key in output_keys:
        csv_info = output_config[out_key].get(CSV_K)
        for table in csv_info:
            file_name = os.path.join(output_path, table + '.csv')
            output_files[table] = file_name
            columns = list(csv_info[table].keys())
            with open(file_name, 'w') as fp:
                csv_writer = csv.writer(fp)
                csv_writer.writerow(columns)

    return output_files


def output_data(output_config, output_keys, output_files, school=None, student_info=None, state_population=None,
                inst_hier=None, batch_guid=None, section=None, assessment=None):
    """
    Output the data to using the configuration information and the relevant objects
    :param output_config: The output configuration dictionary
    :param output_keys: A list of output formats that should be output from the given data
    :param output_files: A dictionary of output paths for each table to be output
    :param state_population: The state population object to use in outputting data
    :param school: The school object to use in outputting data
    :param student_info: the student info object to use to in outputting data
    :return: None
    """
    for o_key in output_keys:
        csv_conf = output_config[o_key][CSV_K]
        for table in csv_conf:

            output_file = output_files[table]
            output_data_list = []
            if student_info:
                for subject in student_info.asmt_scores:
                    output_row = create_output_csv_dict(csv_conf[table], state_population, school,
                                                        student_info, subject, inst_hier, batch_guid, section, assessment)
                    output_data_list.append(output_row) if output_row else None
            else:
                output_row = create_output_csv_dict(csv_conf[table], state_population, school,
                                                    student_info, None, inst_hier, batch_guid, section, assessment)
                output_data_list.append(output_row) if output_row else None
            write_csv_rows(output_file, output_data_list)


def create_output_csv_dict(table_config_dict, state_population, school, student_info, subject, inst_hier, batch_guid, section, assessment):
    """
    Create the csv output dictionary from the given data
    :param table_config_dict: the config dict pertaining directly to the table being output
    :param state_population: The state population object to use in outputting data
    :param school: The school object to use in outputting data
    :param student_info: the student info object to use to in outputting data
    :param subject: the name of the subject to output
    :return: a mapping between column names and values
    """

    output_dict = {}
    idgen = IdGen()

    asmt_score = student_info.asmt_scores[subject] if student_info else None
    claim_scores = asmt_score.claim_scores if asmt_score else None

    obj_name_map = {
        'student_info': student_info,
        'school': school,
        'state': state_population,
        'state_population': state_population,
        'claim_scores': claim_scores,
        'asmt_scores': asmt_score,
        'asmt_score': asmt_score,
        'date_taken': student_info.asmt_dates_taken[subject] if student_info else None,
        'inst_hierarchy': inst_hier,
        'batch_guid': MakeTemp(value=batch_guid),
        'idgen': idgen,
        'UNIQUE_ID': MakeTemp(value=idgen.get_id),
        'section': section,
        'assessment': assessment,
    }

    required_objects = {obj_name.split('.')[0] for obj_name in table_config_dict.values()}

    # if a required object is missing then this table is not meant to be written or there is an error
    # Return None
    for req_obj in required_objects:
        # if the name we are looking for is not present, that value will be used for the column during output
        if obj_name_map.get(req_obj, not None) is None:
            return None

    for column_name in table_config_dict:
        internal_map_string_list = table_config_dict[column_name].split('.')

        obj_name = internal_map_string_list[0]

        data_object = obj_name_map.get(obj_name, MakeTemp(value=obj_name))

        internal_map_string_list = ['value', 'value'] if isinstance(data_object, MakeTemp) else internal_map_string_list

        # remove everything before the first '.' from attribute name
        attribute_name = '.'.join(internal_map_string_list[1:])

        value = get_value_from_object(data_object, attribute_name, subject)
        output_dict[column_name] = value

    return output_dict


def get_value_from_object(data_object, attr_name, subject):
    """
    Using the data object get the value desired and return
    :param data_object: the data object to pull the data from. (could also be a list)
    :param attr_name: Name of the desired attribute
    :param subject: The current subject
    :return: a single cleaned value
    """
    index_attr_list = attr_name.split('.')
    if len(index_attr_list) > 1:
        attr_index, attr_name = index_attr_list
        attr_index = int(attr_index)
        value_list = data_object[attr_index - 1] if len(data_object) > attr_index - 1 else None
        value = getattr(value_list, attr_name)
    else:
        value = getattr(data_object, attr_name)

    # Final value cleanup #
    # if the value is a dictionary, there is a value for each subject
    value = value[subject] if isinstance(value, dict) else value
    # if the value is a date object reformat the value
    value = value.strftime('%Y%m%d') if isinstance(value, date) else value
    # check to see if the value is a callable function
    value = value() if callable(value) else value

    return value


def write_csv_rows(output_path, row_dict_list):
    """
    Write the given list of csv dictionaries to the given file
    :param output_path: the path to the output file
    :param row_dict_list: a list of csv dictionaries
    :return: None
    """
    # may want to pass this value in as a parameter or pull this information
    # from the config file if ordering is to be preserved
    fieldnames = get_header_from_file(output_path)
    with open(output_path, 'a') as fp:
        csv_writer = csv.DictWriter(fp, fieldnames)
        csv_writer.writerows(row_dict_list)


def get_header_from_file(filename):
    """
    Open a csv file and return the first row
    :param filename:
    :return: the header as a list
    """
    with open(filename, 'r') as fp:
        reader = csv.reader(fp)
        header = next(reader)
    return header


class MakeTemp(object):
    def __init__(self, **kwargs):
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

if __name__ == '__main__':
    conf_dict = {
        'lz': {
            'csv': {
                'REALDATA': {
                    'guid_asmt': 'student_info.asmt_guids',
                    'guid_asmt_location': 'school.school_guid',
                    'name_asmt_location': 'school.school_name',
                    'grade_asmt': 'student_info.grade',
                    'name_state': 'state_population.state_name',
                    'code_state': 'state_population.state_code',
                    'guid_district': 'school.district_guid',
                    'name_district': 'school.district_name',
                    'guid_school': 'school.school_guid',
                    'name_school': 'school.school_name',
                    'type_school': 'school.school_category',
                    'guid_student': 'student_info.student_guid',
                    'name_student_first': 'student_info.first_name',
                    'name_student_middle': 'student_info.middle_name',
                    'name_student_last': 'student_info.last_name',
                    'address_student_line1': 'student_info.address_1',
                    'address_student_line2': 'student_info.address_2',
                    'address_student_city': 'student_info.city',
                    'address_student_zip': 'student_info.zip_code',
                    'gender_student': 'student_info.gender',
                    'email_student': 'student_info.email',
                    'dob_student': 'student_info.dob',
                    'grade_enrolled': 'student_info.grade',
                    'score_claim_1': 'claim_scores.1.claim_score',
                    'score_claim_2': 'claim_scores.2.claim_score',
                    'score_claim_3': 'claim_scores.3.claim_score',
                    'date_taken': 'student_info.asmt_dates_taken',
                }
            }
        }
    }

    out_keys = ['lz']
    out_path = os.getcwd()
    out_files = initialize_csv_file(conf_dict, out_keys, out_path)
    print(out_files)
    student_info1 = MakeTemp(asmt_guids=1, student_guid=2, first_name='bill', last_name='nye', middle_name='tom',
                             address_1='1 bob st.', address_2='', city='new york', zip_code=12345, gender='m',
                             email='b.n@email.com', dob='11111999', grade=4, asmt_dates_taken=date.today(),
                             asmt_scores={'math': MakeTemp(claim_scores=[MakeTemp(claim_score=1200), MakeTemp(claim_score=1200),
                                                                         MakeTemp(claim_score=1200), MakeTemp(claim_score=1200)]),
                                          'ela': MakeTemp(claim_scores=[MakeTemp(claim_score=1300), MakeTemp(claim_score=1300),
                                                                        MakeTemp(claim_score=1300)])})
    state1 = MakeTemp(state_name='New York', state_code="NY")
    school1 = MakeTemp(school_guid=123, school_name='school123', district_name='district1', district_guid='d123',
                       school_category='elementary')
    output_data(conf_dict, out_keys, out_files, school1, student_info1, state1)
