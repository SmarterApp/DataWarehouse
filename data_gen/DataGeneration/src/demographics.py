'''
Created on Jul 1, 2013

@author: swimberly
'''

import csv
import random

from generate_names import generate_first_or_middle_name, possibly_generate_middle_name


H_ID = 0
H_GROUPING = 1
H_SUBJECT = 2
H_GRADE = 3
H_DEMOGRAPHIC = 4
H_COL_NAME = 5
H_TOTAL = 6
H_PERF_1 = 7
H_PERF_2 = 8
H_PERF_3 = 9
H_PERF_4 = 10

L_GROUPING = 0
L_TOTAL = 1
L_PERF_1 = 2
L_PERF_2 = 3
L_PERF_3 = 4
L_PERF_4 = 5

ALL_DEM = 'all'


class Demographics(object):
    '''
    '''

    def __init__(self, demo_csv_file):
        self.dem_data = self._parse_file(demo_csv_file)

    def _parse_file(self, file_name):
        '''
        open csv file
        '''

        dem_dict = {}

        with open(file_name) as cfile:
            reader = csv.reader(cfile)

            count = 0
            header = []
            for row in reader:
                if count == 0 and row[0]:
                    header = row
                    count += 1
                elif row[0] and row != header:
                    dem_dict = self._add_row(row, dem_dict)
                    count += 1

        return dem_dict

    def _add_row(self, row_list, dem_dict):
        '''
        Take a row from the csv file and add the data to the demographics dictionary
        '''

        dem_id = row_list[H_ID]

        id_dict = dem_dict.get(dem_id)
        if id_dict:
            subject_dict = id_dict.get(row_list[H_SUBJECT])
            if subject_dict:
                grade_dict = subject_dict.get(row_list[H_GRADE])
                if grade_dict:
                    grade_dict[row_list[H_COL_NAME].lower()] = self._construct_dem_list(row_list)
                else:
                    subject_dict[row_list[H_GRADE].lower()] = {row_list[H_COL_NAME].lower(): self._construct_dem_list(row_list)}
            else:
                id_dict[row_list[H_SUBJECT].lower()] = {row_list[H_GRADE].lower(): {row_list[H_COL_NAME].lower(): self._construct_dem_list(row_list)}}
        else:
            dem_dict[dem_id.lower()] = {row_list[H_SUBJECT].lower(): {row_list[H_GRADE].lower(): {row_list[H_COL_NAME].lower(): self._construct_dem_list(row_list)}}}

        return dem_dict

    def _construct_dem_list(self, row_list):
        '''
        Take a single row from the file and create a demographic dict object
        of the form [GROUPING, TOTAL_PERC, PL1_PERC, PL2_PERC, PL3_PERC, PL4_PERC]
        ie. [1, 20, 20, 40, 20, 20]
        '''
        ret_list = [row_list[H_GROUPING], row_list[H_TOTAL], row_list[H_PERF_1], row_list[H_PERF_2], row_list[H_PERF_3], row_list[H_PERF_4]]
        # convert to ints and return
        return [int(x) for x in ret_list]

    def get_grade_demographics(self, dem_id, subject, grade):
        '''
        Get the demographic data that corresponds to the provided values
        Data is returned in the following format
        {name: [order, tot_percent, pl1_perc, pl2_perc, pl3_perc, pl4_perc], ... }
        {'female': ['1', '49', '8', '31', '49', '12'], ... }
        @param dem_id: The demographic id found in the data file
        @param subject: the name of the subject
        @param grade: the name of the grade
        @return: A dictionary containing list of all dem data.
        @rtype: dict
        '''
        return self.dem_data[dem_id.lower()][subject.lower()][str(grade)]

    def get_grade_demographics_total(self, dem_id, subject, grade):
        '''
        Return only the performance level percentages for the id, subject and grade
        '''
        grade_demo = self.get_grade_demographics(dem_id, subject, grade)
        total_dem = grade_demo[ALL_DEM][L_PERF_1:L_PERF_4 + 1]
        return total_dem

    def assign_demographics(self, asmt_outcomes, students, subject, grade, dem_id):
        '''
        Take fact assessment outcomes and apply demographics to the data based on dem_dict
        @param asmt_outcomdes: the list of all the fact assessments that were created
        '''
        assert len(asmt_outcomes) == len(students)

        # Get the demographics corresponding to the id, subject, grade
        grade_demo = self.get_grade_demographics(dem_id, subject, grade)

        #ordered_keys = sorted(grade_demo, key=lambda key: grade_demo[key][L_GROUPING])
        #print(grade_demo)
        groupings = sorted({grade_demo[x][L_GROUPING] for x in grade_demo})
        total_students = len(asmt_outcomes)

        # Convert percentages to actual values, based on number of students given
        dem_count_dict = percentages_to_values(grade_demo, total_students)

        # Assign Male and Female Gender
        self._make_male_or_female(dem_count_dict['male'], dem_count_dict['female'], asmt_outcomes, students)

        # Removing all and gender
        groupings.remove(0)
        groupings.remove(1)

        # Assign other demographics
        for group in groupings:
            self._make_other_demographics(dem_count_dict, group, asmt_outcomes)

        return asmt_outcomes, students

    def _make_other_demographics(self, grade_count_dict, group, asmt_outcomes):
        '''
        '''
        group_dict = {}

        # filter all items in this group to new dictionary
        for key in grade_count_dict:
            if grade_count_dict[key][L_GROUPING] == group:
                group_dict[key] = grade_count_dict[key][:]

        # Assign students the demographics
        for outcome in asmt_outcomes:
            out_pl = outcome.asmt_perf_lvl
            demographic_set = False

            # loop through available demographics
            # if the value for that perf_lvl is not 0. Give the outcome that demographic
            for demo_key in group_dict:
                pl_index = out_pl + 1  # offset perf_lvl by 1
                if group_dict[demo_key][pl_index]:
                    setattr(outcome, demo_key, 'Y')
                    group_dict[demo_key][pl_index] -= 1
                    demographic_set = True
                    break

            # if no demographic was set, assign demographic randomly
            # only if demographic is grouped with other demographics
            if not demographic_set and len(group_dict) > 1:
                rand_dem = random.choice(list(group_dict.keys()))
                setattr(outcome, rand_dem, 'Y')

        return asmt_outcomes

    def _make_male_or_female(self, male_list, female_list, asmt_outcomes, students):
        '''
        '''
        males = []
        females = []
        male_pl_counts = male_list[L_PERF_1:]
        female_pl_counts = male_list[L_PERF_1:]

        for i in range(len(students)):
            assert students[i].student_guid == asmt_outcomes[i].student_guid
            student_pl = asmt_outcomes[i].asmt_perf_lvl

            if male_pl_counts[student_pl - 1]:
                males.append(students[i])
                male_pl_counts[student_pl - 1] -= 1
            elif female_pl_counts[student_pl - 1]:
                females.append(students[i])
                female_pl_counts[student_pl - 1] -= 1
            else:
                if random.randint(0, 1):
                    males.append(students[i])
                else:
                    females.append(students[i])

        self._assign_gender(males, 'male')
        self._assign_gender(females, 'female')

        return students

    def _assign_gender(self, student_list, gender):
        '''
        '''
        for student in student_list:
            # Check to see if student already has new gender
            if not student.has_updated_gender:
                student.gender = gender
                student.first_name = generate_first_or_middle_name(gender)
                student.middle_name = possibly_generate_middle_name(gender)
                student.has_updated_gender = True


def percentages_to_values(grade_demo_dict, total_records):
    ret_dict = {}

    for k in grade_demo_dict:
        perc_list = grade_demo_dict[k]

        # Grouping
        val_list = [perc_list[L_GROUPING]]  # place first value in list

        # Total
        total_value = int((perc_list[L_TOTAL] / 100) * total_records)
        if total_value == 0:
            total_value += 1
        val_list.append(total_value)

        # Performance Levels
        for i in range(L_PERF_1, L_PERF_4 + 1):
            pl_total = int((perc_list[i] / 100) * total_value)
            val_list.append(pl_total)

        # check that we have enough values
        diff = total_value - sum(val_list[L_PERF_1:L_PERF_4 + 1])

        # randomly add values for the differences
        for i in range(diff):
            l_index = random.randint(L_PERF_1, L_PERF_4)
            val_list[l_index] += 1

        ret_dict[k] = val_list

    return ret_dict


if __name__ == '__main__':

    import json
    dem = Demographics('/Users/swimberly/projects/edware/fixture_data_generation/DataGeneration/datafiles/demographicStats.csv')
    print(json.dumps(dem.dem_data, indent=4))
    print(json.dumps(dem.get_grade_demographics('typical1', 'math', '5'), indent=2))
