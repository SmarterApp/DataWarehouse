"""
The multi-processed data generator for the SBAC project. Ultimately, this version relies heavily on the regular
data generator, but attempts to achieve performance improvements related to using the multiprocess library from Python.

Command line arguments:
  --team TEAM_NAME: Name of team to generate data for (expects sonics or arkanoids)
  --state_name STATE_NAME: Name of state to generate data for (defaults to 'North Carolina')
  --state_code STATE_CODE: Code of state to generate data for (defaults to 'NC')
  --state_type STATE_TYPE_NAME: Name of state type to generate data for (expects devel, typical_1, california)
  --process_count: The number of processes to use to generate data (defaults to 2)

@author: nestep
@date: March 22, 2014
"""

import argparse
import datetime
import multiprocessing
import os
import random
import traceback

from mongoengine import connect
from pymongo import Connection

import generate_data as generate_data
import sbac_data_generation.config.cfg as sbac_in_config
import sbac_data_generation.generators.hierarchy as sbac_hier_gen

from sbac_data_generation.util.id_gen import IDGen

DISTRICT_TOTAL_COUNT = 0
DISTRICT_COMPLETE_COUNT = 0
TOTAL_STUDENT_AVERAGE = 0
CALLBACK_LOCK = multiprocessing.Lock()


def generate_state_district_hierarchy(id_gen):
    """
    Create the the states and districts to generate data for.

    @param id_gen: ID generator
    @returns: A list of tuples suitable to be fed into a worker
    """
    global DISTRICT_TOTAL_COUNT
    district_tuples = []

    # Start with states
    for state_cfg in generate_data.STATES:
        # Create the state object
        state = sbac_hier_gen.generate_state(state_cfg['type'], state_cfg['name'], state_cfg['code'], id_gen)
        print('Created State: %s' % state.name)

        # Grab the assessment rates by subjects
        asmt_skip_rates_by_subject = state.config['subject_skip_percentages']

        # Create the assessment objects
        assessments = {}
        for year in generate_data.ASMT_YEARS:
            for subject in sbac_in_config.SUBJECTS:
                for grade in generate_data.GRADES_OF_CONCERN:
                    # Create the summative assessment
                    asmt_key_summ = str(year) + 'summative' + str(grade) + subject
                    assessments[asmt_key_summ] = generate_data.create_assessment_object('SUMMATIVE', 'Spring', year,
                                                                                        subject, id_gen)

                    # Create the interim assessments
                    for period in generate_data.INTERIM_ASMT_PERIODS:
                        asmt_key_intrm = str(year) + 'interim' + period + str(grade) + subject
                        asmt_intrm = generate_data.create_assessment_object('INTERIM COMPREHENSIVE', period, year,
                                                                            subject, id_gen)
                        assessments[asmt_key_intrm] = asmt_intrm

        # Build the districts
        for district_type, dist_type_count in state.config['district_types_and_counts'].items():
            for _ in range(dist_type_count):
                # Create the district
                district = sbac_hier_gen.generate_district(district_type, state, id_gen)
                print('  Created District: %s (%s District)' % (district.name, district.type_str))
                district_tuples.append((district, assessments, asmt_skip_rates_by_subject))
                DISTRICT_TOTAL_COUNT += 1

    # Return the districts
    return district_tuples


def district_pool_worker(district, assessments, skip_rates, id_lock, id_mdict):
    """
    Process a single district. This is basically a wrapper for generate_data.generate_district_date that is designed to
    be called through a multiprocessor.Pool construct.

    @param district: The district to generate data for
    @param assessments: The assessments to potentially generate
    @param skip_rates: Rates (changes) to skip assessments
    @param id_lock: Monitored lock for ID generator
    @param id_mdict: Monitored dictionary for ID generator
    """
    id_gen = IDGen(id_lock, id_mdict)

    # Note that we are processing
    print('Starting to generate data for district %s (%s District)' % (district.name, district.type_str))

    # Start the processing
    dist_tstart = datetime.datetime.now()
    try:
        count = generate_data.generate_district_data(district.state, district,
                                                     random.choice(generate_data.REGISTRATION_SYSTEM_GUIDS),
                                                     assessments, skip_rates, id_gen)
    except Exception as ex:
        print('%s' % ex)
        traceback.print_exc()
    dist_tend = datetime.datetime.now()
    return district.name, count, (dist_tend - dist_tstart)


def pool_callback(tpl):
    global DISTRICT_COMPLETE_COUNT, TOTAL_STUDENT_AVERAGE
    district_name, student_count, run_time = tpl
    with CALLBACK_LOCK:
        DISTRICT_COMPLETE_COUNT += 1
        TOTAL_STUDENT_AVERAGE += student_count
        print('District %s generated with average of %i students/year in %s (%i of %i)' % (district_name, student_count,
                                                                                           run_time,
                                                                                           DISTRICT_COMPLETE_COUNT,
                                                                                           DISTRICT_TOTAL_COUNT))


if __name__ == '__main__':
    # Argument parsing for task-specific arguments
    parser = argparse.ArgumentParser(description='SBAC data generation task.')
    parser.add_argument('-t', '--team', dest='team_name', action='store', default='sonics',
                        help='Specify the name of the team to generate data for (sonics, arkanoids)',
                        required=False)
    parser.add_argument('-sn', '--state_name', dest='state_name', action='store', default='North Carolina',
                        help='Specify the name of the state to generate data for (default=North Carolina)',
                        required=False)
    parser.add_argument('-sc', '--state_code', dest='state_code', action='store', default='NC',
                        help='Specify the code of the state to generate data for (default=NC)',
                        required=False)
    parser.add_argument('-st', '--state_type', dest='state_type', action='store', default='devel',
                        help='Specify the type of state to generate data for (devel (default), typical_1, california)',
                        required=False)
    parser.add_argument('-pc', '--process_count', dest='process_count', action='store', default='2',
                        help='Specific the number of sub-processes to spawn (default=2)', required=False)
    args, unknown = parser.parse_known_args()

    # Set team-specific configuration options
    generate_data.assign_team_configuration_options(args.team_name, args.state_name, args.state_code, args.state_type)

    # Record current (start) time
    tstart = datetime.datetime.now()

    # Verify output directory exists
    if not os.path.exists(generate_data.OUT_PATH_ROOT):
        os.makedirs(generate_data.OUT_PATH_ROOT)

    # Connect to MongoDB and drop an existing datagen database
    c = Connection()
    if 'datagen' in c.database_names():
        c.drop_database('datagen')

    # Clean output directory
    for file in os.listdir(generate_data.OUT_PATH_ROOT):
        file_path = os.path.join(generate_data.OUT_PATH_ROOT, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except:
            pass

    # Create the ID generator
    manager = multiprocessing.Manager()
    lock = manager.Lock()
    mdict = manager.dict()
    idg = IDGen(lock, mdict)

    # Connect to MongoDB, datagen database
    connect('datagen')

    # Prepare the output files
    generate_data.prepare_output_files(generate_data.YEARS)

    # Create the registration systems
    generate_data.REGISTRATION_SYSTEM_GUIDS = generate_data.build_registration_systems(generate_data.YEARS, idg)

    # Build the states and districts
    districts = generate_state_district_hierarchy(idg)

    # Go
    print()
    print('Processing of districts beginning now')
    pool = multiprocessing.Pool(processes=int(args.process_count))
    for tpl in districts:
        pool.apply_async(district_pool_worker, args=(tpl[0], tpl[1], tpl[2], lock, mdict), callback=pool_callback)
    pool.close()
    pool.join()

    # Record now current (end) time
    tend = datetime.datetime.now()

    # Print statistics
    print()
    print('Average students per year: %i' % TOTAL_STUDENT_AVERAGE)
    print()
    print('Run began at:  %s' % tstart)
    print('Run ended at:  %s' % tend)
    print('Run run took:  %s' % (tend - tstart))
    print()