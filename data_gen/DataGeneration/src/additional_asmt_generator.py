__author__ = 'swimberly'

import os
import argparse
import csv
import json
import datetime
from collections import OrderedDict
import random
import uuid
from time import mktime, strptime

from DataGeneration.src.writers.write_to_csv import create_csv, prepare_csv_files
from DataGeneration.src.models.landing_zone_data_format import (create_helper_entities_from_lz_dict,
                                                                create_realdata_objs_from_helper_entities,
                                                                add_student_realdata_to_dict, RealDataFormat)


ID = 'identification'
TYPE = 'type'
GUID = 'guid'
PERF_LVLS = 'performance_levels'
OVERALL = 'overall'
MIN = 'min_score'
MAX = 'max_score'
CUT_POINT = 'cut_point'
JSON_PATTERN = 'METADATA_ASMT_ID_{}.json'
CSV_PATTERN = 'REALDATA_ASMT_ID_{}.csv'
DATE_TAKEN = 'date_assessed'
DATE_FORMAT = '%Y%m%d'


def update_row(row_dict, perf_change_tup, asmt_type, asmt_dict, json_map, date_change=-3):
    """

    :param row_dict:
    :param perf_change_tup: A tuple containing the range of performance change as percentages.
        ie (10, 15) would be 10 to 15 point increase, where (-15, -10) would be 10 to 15 point decrease
    :param asmt_type:
    :param asmt_dict:
    :param date_change: the number of months to change the date taken by, default is -3 (3 months previous)
    :return:
    """
    old_asmt_guid = row_dict['guid_asmt']
    json_obj = json_map[asmt_dict[old_asmt_guid]]

    # update the date
    date_object = datetime.date.fromtimestamp(mktime(strptime(row_dict[DATE_TAKEN], DATE_FORMAT)))
    row_dict[DATE_TAKEN] = month_delta(date_object, date_change)

    # update the scores
    cut_points = get_cut_points(json_obj)
    row_dict = update_scores(row_dict, perf_change_tup, cut_points)

    # update assessment type and guid
    row_dict['asmt_type'] = asmt_type
    row_dict['guid_asmt'] = asmt_dict[old_asmt_guid]

    return row_dict


def generate_score_offset(perf_change_tup):
    """

    :param perf_change_tup:
    :return:
    """
    offset = random.randint(perf_change_tup[0], perf_change_tup[1])
    return offset if perf_change_tup[0] >= 0 else offset * -1


def update_scores(row_dict, perf_change_tup, cut_points):
    """

    :param row_dict:
    :param perf_change_tup:
    :return:
    """
    offset = generate_score_offset(perf_change_tup)
    row_dict['score_asmt'] = int(row_dict['score_asmt']) + offset
    row_dict['score_asmt_min'] = int(row_dict['score_asmt_min']) + offset
    row_dict['score_asmt_max'] = int(row_dict['score_asmt_max']) + offset
    row_dict['score_perf_level'] = determine_perf_lvl(row_dict['score_asmt'], cut_points)

    for i in range(len(cut_points) + 1):
        offset = generate_score_offset(perf_change_tup)
        row_dict['score_claim_{}'.format(i + 1)] = int(row_dict['score_claim_{}'.format(i + 1)]) + offset
        row_dict['score_claim_{}_max'.format(i + 1)] = int(row_dict['score_claim_{}_max'.format(i + 1)]) + offset
        row_dict['score_claim_{}_min'.format(i + 1)] = int(row_dict['score_claim_{}_min'.format(i + 1)]) + offset

    return row_dict


def get_cut_points(asmt_dict):
    """
    Get a list of the cutpoints from the assessment dictionary
    :param asmt_dict:
    :return:
    """
    min_max_score = [asmt_dict[OVERALL][MIN], asmt_dict[OVERALL][MAX]]
    perf_lvl_dict = asmt_dict[PERF_LVLS]

    return [int(x[CUT_POINT]) for x in perf_lvl_dict.values()
            if x[CUT_POINT] not in min_max_score and x[CUT_POINT] != '']


def determine_perf_lvl(score, cut_points):
    """

    :param score: Asmt score
    :param cut_points: A list of cutpoints that excludes min and max scores
    :return: the performance level
    """

    for i in range(len(cut_points)):
        if score < cut_points[i]:
            return i
    return len(cut_points) + 1


def month_delta(date, delta):
    m, y = (date.month+delta) % 12, date.year + (date.month + delta - 1) // 12
    if not m:
        m = 12
    d = min(date.day,
            [31, 29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date.replace(day=d, month=m, year=y)


def get_header_from_file(csv_file_name):
    """
    Given a filename open the file and return the header
    :param csv_file_name: the path to the file to be opened
    :return: the file header as a list
    """
    with open(csv_file_name, 'r') as fp:
        c_reader = csv.reader(fp)
        header = next(c_reader)
    return header


def create_new_json_file(old_json_filename, asmt_type, output_location):
    """
    Create a new json file using the given information
    :param old_json_filename: the name/path of the json filename
    :type old_json_filename: str
    :param asmt_guid: the new asmt_guid to use
    :param asmt_type: the type of the assessment being created
    """
    with open(old_json_filename, 'r') as fp:
        json_dict = json.load(fp, object_pairs_hook=OrderedDict)

    new_asmt_guid = str(uuid.uuid4())
    old_asmt_guid = json_dict[ID][GUID]
    json_dict[ID][GUID] = new_asmt_guid
    json_dict[ID][TYPE] = asmt_type

    new_filename = os.path.join(output_location, JSON_PATTERN.format(new_asmt_guid))

    with open(new_filename, 'w') as fp:
        json.dump(json_dict, fp, indent=4)

    return json_dict, old_asmt_guid, new_asmt_guid


def read_csv_file(csv_file_name, perf_change_tup, asmt_type, asmt_dict, date_change, output_path, star_format, json_map, batch_size=100000):
    """

    :param csv_file_name:
    :param batch_size:
    :return:
    """

    with open(csv_file_name, 'r') as cf:
        c_creader = csv.DictReader(cf)
        student_list_by_asmt = create_list_of_csv_records(c_creader, batch_size, perf_change_tup, asmt_type, asmt_dict, date_change, json_map)
        while student_list_by_asmt:
            output_data(student_list_by_asmt, output_path, star_format)
            student_list_by_asmt = create_list_of_csv_records(c_creader, batch_size, perf_change_tup, asmt_type, asmt_dict, date_change, json_map)


def create_list_of_csv_records(csv_reader, batch_size, perf_change_tup, asmt_type, asmt_dict, date_change, json_map):
    """

    :param csv_reader:
    :param batch_size:
    :return:
    """
    student_info_by_asmt = {}

    for i in range(batch_size):
        try:
            row_dict = next(csv_reader)
            updated_row = update_row(row_dict, perf_change_tup, asmt_type, asmt_dict, json_map, date_change)
            student_info, state, school = create_helper_entities_from_lz_dict(updated_row)

            asmt_guid = list(student_info.asmt_guids.values())[0]

            if not student_info_by_asmt.get(asmt_guid):
                # init key inside dict
                student_info_by_asmt[asmt_guid] = []

            student_info_by_asmt[asmt_guid].append((state, school, student_info))
        except StopIteration:
            break

    return student_info_by_asmt


def output_data(student_tup_map, output_path, star_format=False):
    """
    :param student_tup_map: a map of lists of tuples of the format:
        {asmt_guid: [(state_obj, school_obj, student_info_object), ...], ...}
    :param star_format:
    :return:
    """

    # Output lz_format
    real_data_dict = {}

    for asmt_guid in student_tup_map:
        for stu_tup in student_tup_map[asmt_guid]:
            read_data_list = create_realdata_objs_from_helper_entities(*stu_tup)
            add_student_realdata_to_dict(read_data_list, real_data_dict, 1, False)

    for asmt_guid, data in real_data_dict.items():
        filename = CSV_PATTERN.format(asmt_guid)
        output_file = os.path.join(output_path, filename)
        create_csv(data, output_file)

    # Output Star format
    if star_format:
        pass


def main(input_csv_list, input_json_list, output_asmt_type, output_dir, month_change, asmt_change_low, asmt_change_hi, positive_change=False, start_format=False):
    """

    :param input_csv_list:
    :param input_json_list:
    :param output_asmt_type:
    :param start_format:
    :param output_dir:
    :return:
    """
    asmt_map = {}
    json_map = {}

    for json_file in input_json_list:
        json_dict, old_guid, new_guid = create_new_json_file(json_file, output_asmt_type, output_dir)
        asmt_map[old_guid] = new_guid
        json_map[new_guid] = json_dict

        # prepare output csv file for lz format
        file_path = os.path.join(output_dir, CSV_PATTERN.format(new_guid))
        prepare_csv_files({RealDataFormat: file_path})

        # TODO: prepare output csv file for star format

    ##
    ##
    if not positive_change:
        asmt_change_low = min(asmt_change_low, -asmt_change_low)
        asmt_change_hi = min(asmt_change_hi, -asmt_change_hi)

    perf_change_tup = tuple(sorted([asmt_change_low, asmt_change_hi]))

    for csv_file in input_csv_list:
        read_csv_file(csv_file, perf_change_tup, output_asmt_type, asmt_map, month_change, output_dir, start_format, json_map)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A script that will read the landing zone file generated for a given"
                                                 "assessment and create (a) new file(s) for another assessment")
    parser.add_argument('-c', '--input-csv', nargs='+', required=True,
                        help='The name of the csv file(s) to use to generate new assessments. '
                             'Supply at least 1 filename')
    parser.add_argument('-j', '--input-json', nargs='+', help='The name of the json file(s) to use to generate new '
                                                              'assessments. Supply at least 1 filename')
    parser.add_argument('-a', '--asmt-type', help='The output assessment type')
    parser.add_argument('--star-format', action='store_true',
                        help='Generate the star schema format in addition to the landing zone format')
    parser.add_argument('-o', '--output-location', default=os.getcwd(),
                        help='The path to the directory where files should be written. Default: current working dir')
    parser.add_argument('-m', '--month-change', default=-3, type=int,
                        help='The number of months to offset the current date of the assessment. Default: -3')
    parser.add_argument('-l', '--score-change-low', type=int, default=30,
                        help='The lower bound on how much to change the assessment scores, default: 30')
    parser.add_argument('-u', '--score-change-high', type=int, default=300,
                        help='The upper bound on how much to change the assessment scores, default: 300')
    parser.add_argument('-p', '--positive-score-change', action='store_true',
                        help='whether score change should be positive or negative')


    args = parser.parse_args()
    print(args)

    main(args.input_csv, args.input_json, args.asmt_type, args.output_location, args.month_change, args.score_change_low,
         args.score_change_high, args.positive_score_change, args.star_format)