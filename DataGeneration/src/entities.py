import random
import string
from idgen import IdGen
from uuid import uuid4
import util


class InstitutionHierarchy:
    '''
    Institution Hierarchy object
    '''

    def __init__(self, number_of_students, student_teacher_ratio, low_grade, high_grade,
                 state_name, state_code, district_id, district_name, school_id, school_name, school_category, from_date, most_recent, row_id=None, to_date=None):
        '''
        Constructor
        '''
        self.number_of_students = number_of_students
        self.student_teacher_ratio = student_teacher_ratio
        self.low_grade = low_grade
        self.high_grade = high_grade

        # Ids can either be given to the constructor or provided by constructor
        # Either way, the row_id field must have a value
        id_generator = IdGen()
        if row_id is None:
            self.row_id = id_generator.get_id()
        else:
            self.row_id = row_id

        self.state_name = state_name
        self.state_code = state_code
        self.district_id = district_id
        self.district_name = district_name
        self.school_id = school_id
        self.school_name = school_name
        self.school_category = school_category
        self.from_date = from_date
        self.to_date = to_date
        self.most_recent = most_recent

    def getRow(self):
        return [self.row_id, self.state_name, self.state_code, self.district_id, self.district_name, self.school_id, self.school_name, self.school_category, self.from_date, self.to_date, self.most_recent]


class Class:
    '''
    NOT PRESENT IN NEW SCHEMA
    Class Object
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


class SectionSubject:
    '''
    SectionSubject Object
    '''
    def __init__(self, section_id, section_name, grade, class_name, subject_name, state_code, district_id, school_id, from_date, most_recent, to_date=None, row_id=None):

        # Ids can either be given to the constructor or provided by constructor
        # Either way, the row_id field must have a value
        id_generator = IdGen()
        if row_id is None:
            self.row_id = id_generator.get_id()
        else:
            self.row_id = row_id

        self.section_id = section_id
        self.section_name = section_name
        self.grade = grade
        self.class_name = class_name
        self.subject_name = subject_name
        self.state_code = state_code
        self.district_id = district_id
        self.school_id = school_id
        self.from_date = from_date
        self.most_recent = most_recent
        self.to_date = to_date

    def getRow(self):
        return [self.row_id, self.section_id, self.section_name, self.grade, self.class_name, self.subject_name, self.state_code, self.district_id, self.school_id, self.from_date, self.to_date, self.most_recent]


class TeacherSection:
    '''
    TeacherSection Object
    '''
    def __init__(self, teacher_section_id, teacher_id, section_id, rel_start_date, rel_end_date=None):
        self.teacher_section_id = teacher_section_id
        self.teacher_id = teacher_id
        self.section_id = section_id
        self.rel_start_date = rel_start_date
        self.rel_end_date = rel_end_date

    def getRow(self):
        return [self.teacher_section_id, self.teacher_id, self.section_id, self.rel_start_date, self.rel_end_date]


class Claim(object):
    '''
    claim information to be used by the assessment object
    '''
    def __init__(self, claim_name, claim_score_min=None, claim_score_max=None):
        self.claim_name = claim_name
        self.claim_score_min = claim_score_min
        self.claim_score_max = claim_score_max


class Assessment:
    '''
    AssessmentType Object
    '''
    def __init__(self, asmt_id, asmt_external_id, asmt_type, asmt_period, asmt_period_year, asmt_version, asmt_grade, asmt_subject, from_date, claim_1=None, claim_2=None, claim_3=None, claim_4=None, asmt_score_min=None, asmt_score_max=None,
                 asmt_perf_lvl_name_1=None, asmt_perf_lvl_name_2=None, asmt_perf_lvl_name_3=None, asmt_perf_lvl_name_4=None, asmt_perf_lvl_name_5=None, asmt_cut_point_1=None, asmt_cut_point_2=None, asmt_cut_point_3=None, asmt_cut_point_4=None,
                 asmt_custom_metadata=None, to_date=None, most_recent=None):
        '''
        Constructor
        '''
        self.asmt_id = asmt_id
        self.asmt_external_id = asmt_external_id
        self.asmt_type = asmt_type
        self.asmt_period = asmt_period
        self.asmt_period_year = asmt_period_year
        self.asmt_version = asmt_version
        self.asmt_grade = asmt_grade
        self.asmt_subject = asmt_subject

        self.claim_1 = claim_1
        self.claim_2 = claim_2
        self.claim_3 = claim_3
        self.claim_4 = claim_4

        self.asmt_perf_lvl_name_1 = asmt_perf_lvl_name_1
        self.asmt_perf_lvl_name_2 = asmt_perf_lvl_name_2
        self.asmt_perf_lvl_name_3 = asmt_perf_lvl_name_3
        self.asmt_perf_lvl_name_4 = asmt_perf_lvl_name_4
        self.asmt_perf_lvl_name_5 = asmt_perf_lvl_name_5
        self.asmt_score_min = asmt_score_min
        self.asmt_score_max = asmt_score_max

        self.asmt_cut_point_1 = asmt_cut_point_1
        self.asmt_cut_point_2 = asmt_cut_point_2
        self.asmt_cut_point_3 = asmt_cut_point_3
        self.asmt_cut_point_4 = asmt_cut_point_4

        self.asmt_custom_metadata = asmt_custom_metadata
        self.from_date = from_date
        self.to_date = to_date
        self.most_recent = most_recent

    def __str__(self):
        '''
        toString Method
        '''

        return ("Assessment:[asmt_type: %s, subject: %s, asmt_type: %s, period: %s, version: %s, grade: %s]" % (self.asmt_type, self.asmt_subject, self.asmt_type, self.asmt_period, self.asmt_version, self.asmt_grade))

    def getRow(self):
        return [self.asmt_id, self.asmt_type, self.asmt_period, self.asmt_period_year, self.asmt_version, self.asmt_grade, self.asmt_subject,
                self.claim_1.claim_name, self.claim_2.claim_name, self.claim_3.claim_name, self.claim_4.claim_name,
                self.asmt_perf_lvl_name_1, self.asmt_perf_lvl_name_2, self.asmt_perf_lvl_name_3, self.asmt_perf_lvl_name_4, self.asmt_perf_lvl_name_5,
                self.asmt_score_min, self.asmt_score_max,
                self.claim_1.claim_score_min, self.claim_1.claim_score_max, self.claim_2.claim_score_min, self.claim_2.claim_score_max,
                self.claim_3.claim_score_min, self.claim_3.claim_score_max, self.claim_4.claim_score_min, self.claim_4.claim_score_max,
                self.asmt_cut_point_1, self.asmt_cut_point_2, self.asmt_cut_point_3, self.asmt_cut_point_4,
                self.asmt_custom_metadata, self.from_date, self.to_date, self.most_recent]


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

    def getRow(self):
        return [self.where_taken_id, self.where_taken_name, self.district_name, self. address_1, self.address_2, self.city_name, self.zip_code, self.state_code, self.country_id]


class AssessmentOutcome(object):
    '''
    Assessment outcome object
    '''
    def __init__(self, asmnt_outcome_id, asmnt_outcome_external_id, assessment, student, inst_hier_id, where_taken, date_taken, asmt_score, asmt_create_date, most_recent):
        self.asmnt_outcome_id = asmnt_outcome_id
        self.asmnt_outcome_external_id = asmnt_outcome_external_id
        self.assessment = assessment
        self.student = student
        self.inst_hier_id = inst_hier_id
        self.where_taken = where_taken
        self.date_taken = date_taken
        self.asmt_score = asmt_score
        self.asmt_create_date = asmt_create_date
        self.most_recent = most_recent

    def calc_perf_lvl(self, score, asmt):
        '''
        calculates a performance level as an integer based on a students overall score and
        the cutoffs for the assessment (0, 1 or 2)
        score -- a score object
        asmt -- an assessment object
        '''
        if score.overall > asmt.asmt_cut_point_3:
            if asmt.asmt_cut_point_4:
                return 3
            else:
                return 2
        elif score.overall > asmt.asmt_cut_point_2:
            return 1
        else:
            return 0

    def getRow(self):
        claims = list(self.asmt_score.claims.items())
        asmt_perf_lvl = self.calc_perf_lvl(self.asmt_score, self.assessment)

        return [self.asmnt_outcome_id, self.where_taken.where_taken_name, self.asmnt_outcome_external_id, self.assessment.asmt_id,
                self.student.student_id, self.student.teacher_id, self.student.state_code,
                self.student.district_id, self.student.school_id, self.student.section_id,
                self.inst_hier_id, self.student.section_subject_id,
                self.where_taken.where_taken_id, self.assessment.asmt_grade, self.student.grade,
                self.date_taken, self.date_taken.day, self.date_taken.month, self.date_taken.year,
                self.asmt_score.overall, self.assessment.asmt_score_min, self.assessment.asmt_score_max, asmt_perf_lvl,
                claims[0][1], self.assessment.claim_1.claim_score_min, self.assessment.claim_1.claim_score_max,
                claims[1][1], self.assessment.claim_2.claim_score_min, self.assessment.claim_2.claim_score_max,
                claims[2][1], self.assessment.claim_3.claim_score_min, self.assessment.claim_3.claim_score_max,
                claims[3][1], self.assessment.claim_4.claim_score_min, self.assessment.claim_4.claim_score_max,
                self.asmt_create_date, self.most_recent]


class StudentTemporalData(object):
    '''
    NOT PRESENT IN NEW SCHEMA
    Object to match the student_tmprl_data table
    '''
    def __init__(self, student_tmprl_id, student_id, grade_id, dist_name, school_id, student_class, section_id):
        self.student_tmprl_id = student_tmprl_id
        self.student_id = student_id
        self.grade_id = grade_id
        self.dist_name = dist_name
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

        return [self.student_tmprl_id, self.student_id, self.effective_date, self.end_date, self.grade_id, self.dist_name, self.school_id, self.student_class.class_id, self.section_id]


class Person(object):
    '''
    Base class for teacher, parent, student
    Right now, it only handles name fields
    '''

    def __init__(self, first_name, last_name, middle_name=None):
        '''
        Constructor
        if email and dob are not specified they are set to dummy values
        '''
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name


class Student(Person):
    '''
    Student Object
    Corresponds to student Table
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

    def getRow(self):
        return [self.student_id, self.student_external_id, self.first_name, self.middle_name, self.last_name, self.address_1, self.address_2, self.city, self.state_code, self.zip_code, self.gender, self.email, self.dob, self.school_id, self.district_id]


class Parent(Person):
    '''
    Parent Object
    Corresponds to parent table
    '''

    def __init__(self, first_name, last_name, address_1, city, state_code, zip_code, parent_id=None, parent_external_id=None, middle_name=None, address_2=None):
        super().__init__(first_name, last_name, middle_name=middle_name)

        # Ids can either be given to the constructor or provided by constructor
        # Either way, both Id fields must have a value
        id_generator = IdGen()
        if parent_id is None:
            self.parent_id = id_generator.get_id()
        else:
            self.parent_id = parent_id
        if parent_external_id is None:
            self.parent_external_id = id_generator.get_id()
        else:
            self.parent_external_id = parent_external_id

        self.address_1 = address_1
        self.address_2 = address_2
        self.city = city
        self.state_code = state_code
        self.zip_code = zip_code

    def __str__(self):
        return ("%s %s %s" % (self.first_name, self.middle_name, self.last_name))

    def getRow(self):
        return [self.parent_id, self.parent_external_id, self.first_name, self.middle_name, self.last_name, self.address_1, self.address_2, self.city, self.state_code, self.zip_code]


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

    def getRow(self):
        return [self.teacher_id, self.teacher_external_id, self.first_name, self.middle_name, self.last_name, self.district_id, self.state_code]


class Staff(Person):
    def __init__(self, first_name, last_name, section_id, hier_user_type, state_code, district_id, school_id, from_date, to_date=None, most_recent=None, middle_name=None, staff_id=None, staff_external_id=None):
        super().__init__(first_name, last_name, middle_name=middle_name)
        idgen = IdGen()
        self.row_id = idgen.get_id()
        if(staff_id):
            self.staff_id = staff_id
        else:
            self.staff_id = idgen.get_id()
        if(staff_external_id):
            self.staff_external_id = staff_external_id
        else:
            self.staff_external_id = uuid4()
        self.section_id = section_id
        self.hier_user_type = hier_user_type
        self.state_code = state_code
        self.district_id = district_id
        self.school_id = school_id
        self.from_date = from_date
        self.to_date = to_date
        self.most_recent = most_recent

    def getRow(self):
        return [self.row_id, self.staff_id, self.staff_external_id, self.first_name, self.middle_name, self.last_name, self.section_id, self.hier_user_type, self.state_code, self.district_id, self.school_id, self.from_date, self.to_date, self.most_recent]


class ExternalUserStudent():
    '''
    ExternalUserStudent Object
    Corresponds to dim_external_user_student table
    '''

    def __init__(self, external_user_student_id, external_user_id, student_id, rel_start_date, rel_end_date=None):

        # Ids can either be given to the constructor or provided by constructor
        # Either way, both Id fields must have a value
        id_generator = IdGen()
        if external_user_student_id is None:
            self.external_user_student_id = id_generator.get_id()
        else:
            self.external_user_student_id = external_user_student_id
        if external_user_id is None:
            self.external_user_id = uuid4()
        else:
            self.external_user_id = external_user_id

        self.student_id = student_id
        self.rel_start_date = rel_start_date
        self.rel_end_date = rel_end_date

    def getRow(self):
        return [self.external_user_student_id, self.external_user_id, self.student_id, self.rel_start_date, self.rel_end_date]


class StudentSection():
    def __init__(self, student, section_id, grade, from_date=None, to_date=None, most_recent=None, teacher_id=None, section_subject_id=None):
        idgen = IdGen()
        self.row_id = idgen.get_id()

        self.student_id = student.student_id
        self.first_name = student.first_name
        self.middle_name = student.middle_name
        self.last_name = student.last_name
        self.address_1 = student.address_1
        self.address_2 = student.address_2
        self.city = student.city
        self.zip_code = student.zip_code
        self.gender = student.gender
        self.email = student.email
        self.dob = util.generate_dob(grade)
        self.section_id = section_id
        self.grade = grade
        self.state_code = student.state_code
        self.district_id = student.district_id
        self.school_id = student.school_id
        self.from_date = from_date
        self.to_date = to_date
        self.most_recent = most_recent

        self.teacher_id = teacher_id
        self.section_subject_id = section_subject_id

    def getRow(self):
        return [self.row_id, self.student_id, self.first_name, self.middle_name, self.last_name, self.address_1, self.address_2,
                self.city, self.zip_code, self.gender, self.email, self.dob, self.section_id, self.grade,
                self.state_code, self.district_id, self.school_id, self.from_date, self.to_date, self.most_recent]


def generate_ramdom_name():
    # temporary
    char_set = string.ascii_uppercase + string.digits
    return(''.join(random.sample(char_set, 10)))
