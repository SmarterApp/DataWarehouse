import argparse
import datetime
import os
import csv
import util_2
import constants_2 as constants
from write_to_csv import create_csv
from importlib import import_module
from generate_entities import (generate_institution_hierarchy, generate_sections, generate_students, generate_multiple_staff,
                               generate_fact_assessment_outcomes, generate_assessments)
from generate_helper_entities import generate_state, generate_district, generate_school, generate_assessment_score, generate_claim_score
from entities_2 import InstitutionHierarchy, Section, Assessment, AssessmentOutcome, \
    Staff, ExternalUserStudent, Student
from generate_scores import generate_overall_scores
from gaussian_distributions import gauss_one


DATAFILE_PATH = os.path.dirname(os.path.realpath(__file__))
components = DATAFILE_PATH.split(os.sep)
DATAFILE_PATH = str.join(os.sep, components[:components.index('DataGeneration') + 1])

ENTITY_TO_PATH_DICT = {InstitutionHierarchy: DATAFILE_PATH + '/datafiles/csv/dim_inst_hier.csv',
                       Section: DATAFILE_PATH + '/datafiles/csv/dim_section.csv',
                       Assessment: DATAFILE_PATH + '/datafiles/csv/dim_asmt.csv',
                       AssessmentOutcome: DATAFILE_PATH + '/datafiles/csv/fact_asmt_outcome.csv',
                       Staff: DATAFILE_PATH + '/datafiles/csv/dim_staff.csv',
                       ExternalUserStudent: DATAFILE_PATH + '/datafiles/csv/external_user_student_rel.csv',
                       Student: DATAFILE_PATH + '/datafiles/csv/dim_student.csv'}

LAST_NAMES = 'last_names'
FEMALE_FIRST_NAMES = 'female_first_names'
MALE_FIRST_NAMES = 'male_first_names'
BIRDS = 'birds'
FISH = 'fish'
MAMMALS = 'mammals'

NAMES_TO_PATH_DICT = {BIRDS: DATAFILE_PATH + '/datafiles/name_lists/birds.txt',
                      FISH: DATAFILE_PATH + '/datafiles/name_lists/fish.txt',
                      MAMMALS: DATAFILE_PATH + '/datafiles/name_lists/mammals.txt'
                     }


def generate_data_from_config_file(config_module):

    # First thing: prep the csv files by deleting their contents and adding appropriate headers
    prepare_csv_files(ENTITY_TO_PATH_DICT)

    # Next, prepare lists that are used to name various entities
    name_list_dictionary = generate_name_list_dictionary(NAMES_TO_PATH_DICT)

    # We're going to use the birds and fish list to name our districts
    district_names_1 = name_list_dictionary[BIRDS]
    district_names_2 = name_list_dictionary[FISH]

    # We're going to use mammals and birds to names our schools
    school_names_1 = name_list_dictionary[MAMMALS]
    school_names_2 = name_list_dictionary[BIRDS]

    # Get information from the config module
    school_types = config_module.get_school_types()
    district_types = config_module.get_district_types()
    state_types = config_module.get_state_types()
    states = config_module.get_states()
    scores_details = config_module.get_scores()

    # Generate Assessment CSV File
    flat_grades_list = get_flat_grades_list(school_types)
    assessments = generate_assessments(flat_grades_list, scores_details[config_module.CUT_POINTS])
    create_csv(assessments, ENTITY_TO_PATH_DICT[Assessment])

    # Iterate over all the states we're supposed to create
    # When we get down to the school level, we'll be able to generate an InstitutionHierarchy object
    for state in states:
        # Pull out basic state information
        state_name = state[config_module.NAME]
        state_code = state[config_module.STATE_CODE]

        # Create state object from gathered info
        current_state = generate_state(state_name, state_code)

        # Pull out information on districts within this state
        state_type_name = state[config_module.STATE_TYPE]
        state_type = state_types[state_type_name]
        district_types_and_counts = state_type[config_module.DISTRICT_TYPES_AND_COUNTS]

        # TODO: should we add some randomness here? What are acceptable numbers? 5-10? 10-20?
        number_of_state_level_staff = 10
        # Create the state-level staff
        state_level_staff = generate_non_teaching_staff(number_of_state_level_staff, state_code=current_state.state_code)

        # Create all the districts for the given state.
        # We don't have a state, district, or school table, but we have an institution_hierarchy table.
        # Each row of this table contains all state, district, and school information.
        # districts_by_type is a dictionary such that:
        # key: <string> The type of district
        # value: <list> A list of district objects
        districts_by_type = generate_district_dictionary(district_types_and_counts, district_names_1, district_names_2)
        # All the InstitutionHierarchy objects for this state will be put in the following list
        state_institution_hierarchies = []
        for district_type_name in districts_by_type.keys():
            districts = districts_by_type[district_type_name]
            district_type = district_types[district_type_name]

            # Pull out school information for this type of district
            # Here we get info on the types of schools to create
            school_types_and_ratios = district_type[config_module.SCHOOL_TYPES_AND_RATIOS]

            # Here we get info on the number of schools to create
            school_counts = district_type[config_module.SCHOOL_COUNTS]

            for district in districts:
                # TODO: should we add some randomness here? What are acceptable numbers? 5-10? 10-20?
                number_of_district_level_staff = 10
                district_level_staff = generate_non_teaching_staff(number_of_district_level_staff, state_code=current_state.state_code,
                                                                   district_guid=district.district_guid)

                schools_by_type = create_school_dictionary(school_counts, school_types_and_ratios,
                                                           school_names_1, school_names_2)
                for school_type_name in schools_by_type.keys():
                    schools = schools_by_type[school_type_name]
                    school_type = school_types[school_type_name]
                    school_type_institution_hierarchies = generate_and_populate_institution_hierarchies(schools, school_type,
                                                                                                        current_state, district, assessments)
                    state_institution_hierarchies += school_type_institution_hierarchies
                create_csv(district_level_staff, ENTITY_TO_PATH_DICT[Staff])
        create_csv(state_level_staff, ENTITY_TO_PATH_DICT[Staff])
        create_csv(state_institution_hierarchies, ENTITY_TO_PATH_DICT[InstitutionHierarchy])


def generate_and_populate_institution_hierarchies(schools, school_type, state, district, assessments):
    institution_hierarchies = []
    for school in schools:
        institution_hierarchy = generate_institution_hierarchy_from_helper_entities(state, district, school)
        institution_hierarchies.append(institution_hierarchy)
        populate_school(institution_hierarchy, school_type, assessments)
    return institution_hierarchies

def populate_school(institution_hierarchy, school_type, assessments):

    # Get student count information from config module
    student_counts = school_type[config_module.STUDENTS]
    student_min = student_counts[config_module.MIN]
    student_max = student_counts[config_module.MAX]
    student_avg = student_counts[config_module.AVG]

    # Get Error Band Information from config_module
    eb_dict = config_module.get_error_band()
    eb_min_perc = eb_dict[config_module.MIN_PERC]
    eb_max_perc = eb_dict[config_module.MAX_PERC]
    eb_rand_adj_lo = eb_dict[config_module.RAND_ADJ_PNT_LO]
    eb_rand_adj_hi = eb_dict[config_module.RAND_ADJ_PNT_HI]

    # Get scoring information from config module
    performance_level_dist = config_module.get_performance_level_distributions()
    scores_details = config_module.get_scores()

    grades = school_type[config_module.GRADES]

    students_in_school = []
    sections_in_school = []
    staff_in_school = []
    # TODO: should we add some randomness here? What are acceptable numbers? 5-10? 10-20?
    number_of_school_level_staff = 5
    school_level_staff = generate_non_teaching_staff(number_of_school_level_staff, state_code=institution_hierarchy.state_code,
                                                     district_guid=institution_hierarchy.district_guid, school_guid=institution_hierarchy.school_guid)
    staff_in_school += school_level_staff
    for grade in grades:
        asmt_outcomes_for_grade = []
        number_of_students_in_grade = calculate_number_of_students(student_min, student_max, student_avg)
        for subject_name in constants.SUBJECTS:
            number_of_sections = calculate_number_of_sections(number_of_students_in_grade)
            sections_in_grade = generate_sections(number_of_sections, subject_name, grade, institution_hierarchy.state_code,
                                                  institution_hierarchy.district_guid, institution_hierarchy.school_guid)
            sections_in_school += sections_in_grade
            score_list = generate_list_of_scores(number_of_students_in_grade, scores_details, performance_level_dist, subject_name, grade)
            for section in sections_in_grade:
                # TODO: More accurate math for num_of_students
                # TODO: Do we need to account for the percentages of kids that take ELA or MATH here?
                number_of_students_in_section = number_of_students_in_grade // number_of_sections
                # TODO: Set up district naming like PeopleNames to remove the following line (which is also called in generate_data)
                name_list_dictionary = generate_name_list_dictionary(NAMES_TO_PATH_DICT)
                students_in_section = generate_students_from_institution_hierarchy(number_of_students_in_section, institution_hierarchy, grade, section.section_guid, name_list_dictionary[BIRDS])
                students_in_school += students_in_section
                # TODO: should we add some randomness here? What are acceptable numbers? 1-2? 1-3?
                number_of_staff_in_section = 1
                teachers_in_section = generate_teaching_staff_from_institution_hierarchy(number_of_staff_in_section, institution_hierarchy, section.section_guid)
                staff_in_school += teachers_in_section
                assessment = select_assessment_from_list(assessments, grade, subject_name)
                teacher_guid = teachers_in_section[0].staff_guid
                asmt_outcomes_in_section = generate_assessment_outcomes_from_helper_entities_and_lists(students_in_section, score_list, teacher_guid, section, institution_hierarchy, assessment,
                                                                                                      eb_min_perc, eb_max_perc, eb_rand_adj_lo, eb_rand_adj_hi)
                asmt_outcomes_for_grade.extend(asmt_outcomes_in_section)
        create_csv(asmt_outcomes_for_grade, ENTITY_TO_PATH_DICT[AssessmentOutcome])
    create_csv(students_in_school, ENTITY_TO_PATH_DICT[Student])
    create_csv(sections_in_school, ENTITY_TO_PATH_DICT[Section])
    create_csv(staff_in_school, ENTITY_TO_PATH_DICT[Staff])


def prepare_csv_files(entity_to_path_dict):
    for entity in entity_to_path_dict:
        path = entity_to_path_dict[entity]
        # By opening the file for writing, we implicitly delete the file contents
        with open(path, 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            # Here we write the header the the given entity
            csv_writer.writerow(entity.getHeader())


def generate_name_list_dictionary(list_name_to_path_dictionary):
    name_list_dictionary = {}
    for list_name in list_name_to_path_dictionary:
        path = list_name_to_path_dictionary[list_name]
        name_list = util_2.create_list_from_file(path)
        name_list_dictionary[list_name] = name_list
    return name_list_dictionary


def generate_district_dictionary(district_types_and_counts, district_names_1, district_names_2):
    district_dictionary = {}
    for district_type in district_types_and_counts:
        district_count = district_types_and_counts[district_type]
        district_list = []
        for i in range(district_count):
            district = generate_district(district_names_1, district_names_2)
            district_list.append(district)
        district_dictionary[district_type] = district_list
    return district_dictionary


def create_school_dictionary(school_counts, school_types_and_ratios, school_names_1, school_names_2):
    num_schools_min = school_counts[config_module.MIN]
    num_schools_avg = school_counts[config_module.AVG]
    num_schools_max = school_counts[config_module.MAX]
    # TODO: Can we assume number of schools is a normal distribution?
    number_of_schools_in_district = calculate_number_of_schools(num_schools_min, num_schools_avg, num_schools_max)

    ratio_sum = sum(school_types_and_ratios.values())
    ratio_unit = max((number_of_schools_in_district // ratio_sum), 1)

    school_dictionary = {}
    for school_type_name in school_types_and_ratios:
        # Get the ratio so we can calculate the number of school types to create for each district
        school_type_ratio = school_types_and_ratios[school_type_name]
        number_of_schools_for_type = school_type_ratio * ratio_unit
        school_list = []
        for i in range(number_of_schools_for_type):
            school = generate_school(school_type_name, school_names_1, school_names_2)
            school_list.append(school)
        school_dictionary[school_type_name] = school_list
    return school_dictionary


def generate_institution_hierarchy_from_helper_entities(state, district, school):
    state_name = state.state_name
    state_code = state.state_code
    district_guid = district.district_guid
    district_name = district.district_name
    school_guid = school.school_guid
    school_name = school.school_name
    school_category = school.school_category
    # TODO: generate from_date more intelligently
    from_date = datetime.date.today().strftime('%Y%m%d')
    # TODO: generate most_recent more intelligently
    most_recent = True

    institution_hierarchy = generate_institution_hierarchy(state_name, state_code,
                                                           district_guid, district_name,
                                                           school_guid, school_name, school_category,
                                                           from_date, most_recent)
    return institution_hierarchy


def generate_list_of_scores(total, score_details, perf_lvl_dist, subject_name, grade):

    print('generating %s scores' % total)
    min_score = score_details[config_module.MIN]
    max_score = score_details[config_module.MAX]
    percentage = perf_lvl_dist[subject_name][str(grade)][config_module.PERCENTAGES]
    # The cut_points in score details do not include min and max score. The score generator needs the min and max to be included
    cut_points = score_details[config_module.CUT_POINTS]
    inclusive_cut_points = [min_score]
    inclusive_cut_points.extend(cut_points)
    inclusive_cut_points.append(max_score)

    scores = generate_overall_scores(percentage, inclusive_cut_points, min_score, max_score, total)
    return scores


def generate_assessment_outcomes_from_helper_entities_and_lists(students, scores, teacher_guid, section, institution_hierarchy, assessment, ebmin, ebmax, rndlo, rndhi):

    # The cut_points in score details do not include min and max score. The score generator needs the min and max to be included
    cut_points = [assessment.asmt_cut_point_1, assessment.asmt_cut_point_2, assessment.asmt_cut_point_3]
    if assessment.asmt_cut_point_4:
        cut_points.append(assessment.asmt_cut_point_4)

    asmt_scores = translate_scores_to_assessment_score(scores, cut_points, assessment, ebmin, ebmax, rndlo, rndhi)
    asmt_rec_id = assessment.asmt_rec_id
    state_code = institution_hierarchy.state_code
    district_guid = institution_hierarchy.district_guid
    school_guid = institution_hierarchy.school_guid
    section_guid = section.section_guid
    inst_hier_rec_id = institution_hierarchy.inst_hier_rec_id
    section_rec_id = section.section_rec_id
    where_taken_id = school_guid
    where_taken_name = institution_hierarchy.school_name
    asmt_grade = section.grade
    enrl_grade = section.grade
    date_taken = datetime.date.today()

    asmt_outcomes = generate_fact_assessment_outcomes(students, asmt_scores, asmt_rec_id, teacher_guid, state_code,
                                                      district_guid, school_guid, section_guid, inst_hier_rec_id,
                                                      section_rec_id, where_taken_id, where_taken_name, asmt_grade,
                                                      enrl_grade, date_taken)

    return asmt_outcomes


def translate_scores_to_assessment_score(scores, cut_points, assessment, ebmin, ebmax, rndlo, rndhi):
    score_list = []

    score_min = assessment.asmt_score_min
    score_max = assessment.asmt_score_max

    for score in scores:
        perf_lvl = None
        for i in range(len(cut_points)):
            if score < cut_points[i]:
                perf_lvl = i + 1  # perf lvls are >= 1
                break

        interval_max = calculate_error_band(score, score_min, score_max, ebmin, ebmax, rndlo, rndhi)
        interval_min = -interval_max
        claim_scores = calcuate_claim_scores(score, assessment, interval_max)
        asmt_create_date = datetime.date.today().strftime('%Y%m%d')
        asmt_score = generate_assessment_score(score, perf_lvl, interval_min, interval_max, claim_scores, asmt_create_date)

        score_list.append(asmt_score)
    return score_list


def generate_students_from_institution_hierarchy(number_of_students, institution_hierarchy, grade, section_guid, street_names):
    state_code = institution_hierarchy.state_code
    district_guid = institution_hierarchy.district_guid
    school_guid = institution_hierarchy.school_guid
    school_name = institution_hierarchy.school_name
    students = generate_students(number_of_students, section_guid, grade, state_code, district_guid, school_guid, school_name, street_names)
    return students


def generate_teaching_staff_from_institution_hierarchy(number_of_staff, institution_hierarchy, section_guid):
    state_code = institution_hierarchy.state_code
    district_guid = institution_hierarchy.district_guid
    school_guid = institution_hierarchy.school_guid
    hier_user_type = 'Teacher'
    staff_list = generate_multiple_staff(number_of_staff, hier_user_type, state_code, district_guid, school_guid, section_guid)
    return staff_list


def generate_non_teaching_staff(number_of_staff, state_code='NA', district_guid='NA', school_guid='NA'):
    hier_user_type = 'Staff'
    staff_list = generate_multiple_staff(number_of_staff, hier_user_type, state_code, district_guid, school_guid)
    return staff_list


def calculate_number_of_schools(num_schools_min, num_schools_avg, num_schools_max):
    # TODO: implement me
    return 10


def calculate_number_of_students(student_min, student_max, student_avg):
    # TODO: implement me
    number_of_students = gauss_one(student_min, student_max, student_avg)
    return int(number_of_students)


def calculate_number_of_sections(number_of_students):
    # TODO: Figure out how to calculate number_of_sections
    return 1


def calcuate_claim_scores(score, assessment, interval):
    claim_score_interval_maximum = interval
    claim_score_interval_minimum = -interval
    claim1 = generate_claim_score(score, claim_score_interval_minimum, claim_score_interval_maximum)
    claim2 = generate_claim_score(score, claim_score_interval_minimum, claim_score_interval_maximum)
    claim3 = generate_claim_score(score, claim_score_interval_minimum, claim_score_interval_maximum)
    claim4 = None

    claims = [claim1, claim2, claim3]
    if assessment.asmt_claim_4_score_min:
        claim4 = generate_claim_score(score, claim_score_interval_minimum, claim_score_interval_maximum)
        claims.append(claim4)

    return claims


def get_flat_grades_list(school_config):
    grades = []

    for school_type in school_config:
        grades.extend(school_config[school_type][config_module.GRADES])

    return grades


def select_assessment_from_list(asmt_list, grade, subject):
    for asmt in asmt_list:
        if asmt.asmt_grade == grade and asmt.asmt_subject == subject:
            return asmt


def calculate_error_band(score, smin, smax, ebmin, ebmax, rndlo, rndhi, clip=True):
    assert(smin > 0 and smax > smin)
    assert(score >= smin and score <= smax)
    assert(ebmin > 0 and ebmax > ebmin)
    srange = smax - smin        # score range (from MIN to MAX)
    scenter = smin + srange / 2   # center of score range
    ebsteps = srange / 2        # number of EB steps (= range/2)
    ebrange = ebmax - ebmin     # range of error band sizes
    eb_size_per_step = ebrange / ebsteps    # EB size per step
    dist_from_center = abs(score - scenter)
    ebhalf = ebmin + (eb_size_per_step * dist_from_center)
    return ebhalf


if __name__ == '__main__':
    # Argument parsing
    parser = argparse.ArgumentParser(description='Generate fixture data from a configuration file.')
    parser.add_argument('--config', dest='config_module', action='store', default='dg_types',
                        help='Specify the configuration module that informs that data creation process.', required=False)
    args = parser.parse_args()

    t1 = datetime.datetime.now()
    config_module = import_module(args.config_module)
    generate_data_from_config_file(config_module)
    t2 = datetime.datetime.now()

    print("data_generation starts ", t1)
    print("data_generation ends   ", t2)
