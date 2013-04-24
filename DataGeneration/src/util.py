import random
import constants as constants
import datetime


def generate_district_name(list_1, list_2, max_name_length=None):
    '''
    Generate a name for a district by combining a word from each provided list, taking length into consideration

    @type list_1: list
    @param list_1: a list of strings to use as a component of a district name
    @type list_2: list
    @param list_2: a list of strings to use as a component of a district name
    @type max_name_length: int
    @param max_name_length: The length of the longest acceptable name
    '''
    # TODO: Decouple constants from this function
    suffix = random.choice(constants.DISTRICT_SUFFIX)
    # adding the plus 1 to account for the space between the name and the suffix
    suffix_length = len(suffix) + 1
    if max_name_length:
        max_name_length = max_name_length - suffix_length
        if max_name_length < 0:
            raise Exception('Maximum district name length is too small. Please increase and try again.')
    district_name = generate_name_from_lists(list_1, list_2, max_name_length)
    return district_name + ' ' + suffix


def generate_school_name(school_type, list_1, list_2, max_name_length=None):
    '''
    Generate a name for a school by combining a word from each provided list, taking length into consideration

    @type school_type: str
    @param school_type: (High School, Middle School, Elementary School) used to determine appropriate suffix for name.
    @type list_1: list
    @param list_1: a list of strings to use as a component of a school name
    @type list_2: list
    @param list_2: a list of strings to use as a component of a school name
    @type max_name_length: int
    @param max_name_length: The length of the longest acceptable name
    '''
    # TODO: Decouple constants from this function
    suffix_list = constants.SCHOOL_TYPE_TO_SUFFIXES[school_type]
    suffix = random.choice(suffix_list)
    # adding the plus 1 to account for the space between the name and the suffix
    suffix_length = len(suffix) + 1
    if max_name_length:
        # Need to account for the length of the suffix
        max_name_length = max_name_length - suffix_length
        if max_name_length < 0:
            raise Exception('Maximum school name length is too small. Please increase and try again.')
    school_name = generate_name_from_lists(list_1, list_2, max_name_length)
    return school_name + ' ' + suffix


def generate_name_from_lists(list_1, list_2, max_name_length=None):
    '''
    Generate a name by combining a word from each provided list, taking length into consideration

    @type list_1: list
    @param list_1: a list of strings to use as a component of a name
    @type list_2: list
    @param list_2: a list of strings to use as a component of a name
    @type max_name_length: int
    @param max_name_length: The length of the longest acceptable name
    '''
    name_1 = str(random.choice(list_1))
    name_2 = str(random.choice(list_2))
    result = name_1 + ' ' + name_2
    if max_name_length and (len(result) > max_name_length):
        result = result[:max_name_length]
    return result


def create_list_from_file(file_path):
    with open(file_path, 'r') as name_file:
        lines = name_file.readlines()
        names = []
        for line in lines:
            names.append(line.strip())
    return names


def generate_address(word_list):
    address = str(random.randint(1, 1000))
    street = random.choice(word_list)
    full_address = (address + " " + street + " " + random.choice(constants.ADD_SUFFIX)).title()
    return full_address


def generate_email_address(first_name, last_name, domain):
    domain = '@' + domain.replace(' ', '') + '.edu'
    address = first_name + '.' + last_name
    return (address + domain).lower()


def generate_dob(grade):
    aprox_age = grade + 6
    current_year = int(datetime.datetime.now().year)
    birth_year = current_year - aprox_age
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    dob = datetime.date(birth_year, birth_month, birth_day).strftime("%Y%m%d")
    return dob


def generate_date_given_assessment(assessment):
    year = assessment.asmt_period_year
    period = chop_year_off_asmt_period(assessment.asmt_period)
    month = random.choice(constants.ASSMT_PERIOD_TO_MONTHS_DICT[period])
    max_date = get_max_date_from_month(month)
    day = random.choice(range(1, max_date + 1))
    return datetime.date(year, month, day)

# TODO: replace this function with a dictionary in constants.py
def get_max_date_from_month(month):
    # Ensure month is valid
    assert month in range(1, 13)
    if month == 2:
        return 28
    elif month in [9, 4, 5, 11]:
        return 30
    return 31


def chop_year_off_asmt_period(asmt_period):
    component_strings = asmt_period.split()
    return component_strings[0]
