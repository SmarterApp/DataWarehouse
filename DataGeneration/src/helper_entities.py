import random
from entities import Person
from idgen import IdGen
from entities import Person
from idgen import IdGen
from entities import InstitutionHierarchy
from datetime import date


class State:
    '''
    state object
    '''

    def __init__(self, state_code, state_name, num_of_dist):
        '''
        Constructor
        '''
        self.state_code = state_code
        self.state_name = state_name
        self.num_of_dist = num_of_dist
        self.state_code = state_code

    def __str__(self):
        '''
        String method
        '''
        return ("State:[state_code: %s, state_name:%s, num_of_dist: %s]" % (self.state_code, self.state_name, self.num_of_dist))


class District:
    '''
    District object
    '''

    def __init__(self, district_id, district_name, state_code, state_name, number_of_schools, city_zip_map, wheretaken_list=None):
        '''
        Constructor
        '''
        self.district_id = district_id
        self.district_name = district_name
        self.state_code = state_code
        self.state_name = state_name

        self.number_of_schools = number_of_schools
        self.city_zip_map = city_zip_map
        self.wheretaken_list = wheretaken_list

    def __str__(self):
        '''
        String method
        '''
        return ("District:[district_id: %s, district_name: %s]" % (self.district_id, self.district_name))

"""
class School:
    '''
    School object
    '''
    def __init__(self, school_id, school_name, school_category, district_name, district_id, state_code, state_name, number_of_students, student_teacher_ratio, low_grade, high_grade):
        '''
        Constructor
        '''
        self.school_id = school_id
        self.school_name = school_name
        self.school_category = school_category
        self.district_id = district_id
        self.district_name = district_name
        self.state_code = state_code
        self.state_name = state_name
        self.number_of_students = number_of_students
        self.student_teacher_ratio = student_teacher_ratio
        self.low_grade = low_grade
        self.high_grade = high_grade

    def covert_to_institution_hierarchy(self):

        institution_hierarchy_params = {
            'state_name': self.district_name,
            'state_code': self.state_code,
            'district_id': self.district_id,
            'district_name': self.district_name,
            'school_id': self.school_id,
            'school_name': self.school_name,
            'school_category': self.school_category,
            'from_date': date(2012, 9, 1),
            'to_date': date(2999, 12, 31),
            'most_recent': True
        }

        return InstitutionHierarchy(**institution_hierarchy_params)
"""


class Claim(object):
    '''
    claim information to be used by the assessment object
    '''
    def __init__(self, claim_name, claim_score_min=None, claim_score_max=None):
        self.claim_name = claim_name
        self.claim_score_min = claim_score_min
        self.claim_score_max = claim_score_max


class Score:
    '''
    Score object
    '''
    def __init__(self, overall, claims):
        '''
        Constructor
        '''
        self.overall = overall
        self.claims = claims
        # self.level = level

    def __str__(self):
        '''
        String method
        '''
        return ("Score:[overall: %s, claims: %s]" % (self.overall, self.claims))


class WhereTaken:
    '''
    Where-taken object
    '''
    def __init__(self, where_taken_id, where_taken_name, district_name=None, address_1=None, city_name=None, zip_code=None, state_code=None, country_id=None, address_2=None):
        '''
        wheretaken_id, wheretaken_name, distr.district_name, address_1, city_name, zip_code, distr.state_code, 'US'
        Constructor
        '''
        self.where_taken_id = where_taken_id
        self.where_taken_name = where_taken_name
        self.district_name = district_name
        self.address_1 = address_1
        self.city_name = city_name
        self.zip_code = zip_code
        self.state_code = state_code
        self.country_id = country_id
        self.address_2 = address_2

    def __str__(self):
        '''
        String method
        '''
        return ("WhereTaken:[wheretaken_id: %s, wheretaken_name: %s, district_name: %s, address_1: %s, address_2: %s,city_name:%s, zip_code:%s, state_code :%s, country_id: %s]" % (self.wheretaken_id, self.wheretaken_name, self.district_name, self. address_1, self.address_2, self.city_name, self.zip_code, self.country_id))


class Teacher(Person):
    '''
    Teacher Object
    Corresponds to teacher table
    '''

    def __init__(self, first_name, last_name, district_id, state_code, teacher_id=None, teacher_external_id=None, middle_name=None):
        super().__init__(first_name, last_name, middle_name=middle_name)
        # Ids can either be given to the constructor or provided by constructor
        # Either way, both Id fields must have a value

        id_generator = IdGen()

        if teacher_id is None:
            self.teacher_id = id_generator.get_id()
        else:
            self.teacher_id = teacher_id
        if teacher_external_id is None:
            self.teacher_external_id = id_generator.get_id()
        else:
            self.teacher_external_id = teacher_external_id

        self.district_id = district_id
        self.state_code = state_code

    def __str__(self):
        return ("%s %s %s" % (self.first_name, self.middle_name, self.last_name))


# TODO: Need to clarify the distinction between student and student_section
class Student(Person):
    '''
    Student Object
    '''

    def __init__(self, student_id, student_external_id, first_name, last_name, address_1, dob, district, state, gender, email, school, middle_name=None, address_2=None):

        super().__init__(first_name, last_name, middle_name=middle_name)

        # Ids can either be given to the constructor or provided by constructor
        # Either way, both Id fields must have a value
        id_generator = IdGen()
        if student_id is None:
            self.student_id = id_generator.get_id()
        else:
            self.student_id = student_id
        if student_external_id is None:
            self.student_external_id = id_generator.get_id()
        else:
            self.student_external_id = student_external_id

        # TODO: We probably want to select cities/zips in a more intelligent way
        city_zip_map = district.city_zip_map
        city = random.choice(list(city_zip_map.keys()))
        zip_range = city_zip_map[city]
        zip_code = random.randint(zip_range[0], zip_range[1])

        self.address_1 = address_1
        self.address_2 = address_2
        self.dob = dob
        self.district_id = district.district_id
        self.city = city
        self.state_code = state.state_code
        self.zip_code = zip_code
        self.gender = gender
        self.email = email
        self.school_id = school.school_id

    def __str__(self):
        return ("%s %s %s" % (self.first_name, self.middle_name, self.last_name))
