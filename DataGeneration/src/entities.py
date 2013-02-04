import random
import string


class State:
    '''
    state object
    '''

    def __init__(self, state_id, state_name, num_of_dist):
        '''
        Constructor
        '''
        self.state_id = state_id
        self.state_name = state_name
        self.num_of_dist = num_of_dist

    def __str__(self):
        '''
        String method
        '''
        return ("State:[state_id: %s, state_name:%s, num_of_dist: %s]" % (self.state_id, self.state_name, self.num_of_dist))

    def getRow(self):
        return [self.state_id, self.state_name]


class District:
    '''
    District object
    '''
    # total_id = 0
    def __init__(self, dist_id, state_name, dist_name, num_of_schools, address_1, school_type_in_dist, zipcode_range, city_names, category):
        '''
        Constructor
        '''
        # self.dist_id   = District.total_id
        # District.total_id = District.total_id + 1
        self.dist_id = dist_id
        self.state_name = state_name
        self.dist_name = dist_name
        self.num_of_schools = num_of_schools
        self.address_1 = address_1
        self.school_type_in_dist = school_type_in_dist
        self.zipcode_range = zipcode_range
        self.city_names = city_names
        self.category = category

    def __str__(self):
        '''
        String method
        '''
        return ("District:[dist_id: %s, state_name: %s, num_of_schools: %s, dist_name: %s, address_1: %s, school_type_in_dist: %s]" % (self.dist_id, self.state_name, self.num_of_schools, self.dist_name, self.address_1, self.school_type_in_dist))

    def getRow(self):
        return [self.dist_id, self.category, self.dist_name, self.address_1]


class School:
    '''
    School object
    '''
    # total_id = 0
    def __init__(self, sch_id, dist_id, school_name, num_of_student, stu_tea_ratio, address1, school_type, low_grade, high_grade, place_id, category):
        '''
        Constructor
        '''
        # self.dist_id   = District.total_id
        # District.total_id = District.total_id + 1
        self.sch_id = sch_id
        self.dist_id = dist_id
        self.school_name = school_name
        self.num_of_student = num_of_student
        self.stu_tea_ratio = stu_tea_ratio
        self.address1 = address1
        self.school_type = school_type
        self.low_grade = low_grade
        self.high_grade = high_grade
        self.category = category

        # place_id is where_taken_id
        self.place_id = place_id

    def __str__(self):
        '''
        String method
        '''
        return ("School:[sch_id: %s, dist_id: %s, num_of_student: %s, stu_tea_ratio: %s, school_name: %s, address1: %s, school_type: %s, low_grade: %s, high_grade: %s, place_id:%s]" % (self.sch_id, self.dist_id, self.num_of_student, self.stu_tea_ratio, self.school_name, self.address1, self.school_type, self.low_grade, self.high_grade, self.place_id))

    def getRow(self):
        return [self.sch_id, self.category, self.school_name, self.address1]


class Class:
    '''
    Student object
    '''
    # total_id = 0
    def __init__(self, class_id, title, sub_name, section_stu_map, section_tea_map):
        '''
        Constructor
        '''
        # self.dist_id   = District.total_id
        # District.total_id = District.total_id + 1
        self.class_id = class_id
        self.title = title
        self.sub_name = sub_name
        self.section_stu_map = section_stu_map
        self.section_tea_map = section_tea_map

    def __str__(self):
        '''
        String method
        '''
        return ("Class:[class_id: %s, title: %s, sub_name: %s, section_stu_map: %s, section_tea_map: %s]" % (self.class_id, self.title, self.sub_name, self.section_stu_map, self.section_tea_map))

    def getRow(self):
        return [self.class_id, self.title]


class AssessmentType:
    '''
    AssessmentType Object
    '''
    def __init__(self, assmt_id, subject, assmt_type, period, version, grade):
        '''
        Constructor
        '''
        self.assmt_id = assmt_id
        self.subject = subject
        self.assmt_type = assmt_type
        self.period = period
        self.version = version
        self.grade = grade

    def __str__(self):
        '''
        toString Method
        '''

        return ("Assessment:[assmt_type: %s, subject: %s, assmt_type: %s, period: %s, version: %s, grade: %s]" % (self.assmt_type, self.subject, self.assmt_type, self.period, self.version, self.grade))

    def getRow(self):
        return [self.assmt_id, self.subject, self.assmt_type, self.period, self.version, self.grade]


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
    def __init__(self, place_id, address_1, address_2, address_3, city, state, zip, country):
        '''
        Constructor
        '''
        self.place_id = place_id
        self.address_1 = address_1
        self.address_2 = address_2
        self.address_3 = address_3
        self.city = city
        self.state = state
        self.zip = zip
        self.country = country

    def __str__(self):
        '''
        String method
        '''
        return ("WhereTaken:[place_id: %s, address_1: %s, city: %s, state:%s, zip: %s, country: %s]" % (self.place_id, self.address_1, self.city, self.state, self.zip, self.country))

    def getRow(self):
        return [self.place_id, self.address_1, self.address_2, self.address_3, self.city, self.state, self.zip, self.country]


class AssessmentOutcome(object):
    '''
    Assessment outcome object
    Should map to the fact_asmt_outcome table
    '''
    def __init__(self, asmnt_out_id, asmnt_type_id, student_id, stdnt_tmprl_id, teacher_id, date_taken, date_taken_day, date_taken_month, date_taken_year,
                 where_taken_id, score, asmt_create_date):

        self.asmnt_out_id = asmnt_out_id
        self.asmnt_type_id = asmnt_type_id
        self.student_id = student_id
        self.stdnt_tmprl_id = stdnt_tmprl_id
        self.teacher_id = teacher_id
        self.date_taken = date_taken
        self.date_taken_day = date_taken_day
        self.date_taken_month = date_taken_month
        self.date_taken_year = date_taken_year
        self.where_taken_id = where_taken_id
        self.score = score
        self.asmt_create_date = asmt_create_date

    def getRow(self):
        claims = list(self.score.claims.items())

        return [self.asmnt_out_id, self.asmnt_type_id, self.student_id, self.stdnt_tmprl_id, self.teacher_id, self.date_taken, self.date_taken_day, self.date_taken_month, self.date_taken_year,
                self.where_taken_id, self.score.overall, claims[0][0], claims[0][1], claims[1][0], claims[1][1], claims[2][0], claims[2][1], claims[3][0], claims[3][1], self.asmt_create_date]


class StudentTemporalData(object):
    '''
    Object to match the student_tmprl_data table
    '''
    def __init__(self, student_tmprl_id, student_id, grade_id, district_id, school_id, student_class, section_id):
        self.student_tmprl_id = student_tmprl_id
        self.student_id = student_id
        self.grade_id = grade_id
        self.district_id = district_id
        self.school_id = school_id
        self.student_class = student_class
        self.section_id = section_id
        self.effective_date = None
        self.end_date = None

    def getRow(self):
        eff_date = self.effective_date
        end_date = self.end_date

        if eff_date is None:
            eff_date = ''
        if end_date is None:
            end_date = ''

        return [self.student_tmprl_id, self.student_id, self.effective_date, self.end_date, self.grade_id, self.district_id, self.school_id, self.student_class.class_id, self.section_id]


def generate_ramdom_name():
    # temporary
    char_set = string.ascii_uppercase + string.digits
    return(''.join(random.sample(char_set, 10)))
