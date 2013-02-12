import random
from constants import ADD_SUFFIX
import datetime


def generate_email_address(first_name, last_name, domain):
    domain = '@' + domain.replace(' ', '') + '.edu'
    address = first_name + '.' + last_name
    return address + domain

def generate_address(word_list):
    address = str(random.randint(1, 1000))
    street = random.choice(word_list)
    full_address = address + " " + street + " " + random.choice(ADD_SUFFIX)

    return full_address

def generate_dob(grade):

    aprox_age = grade + 6
    current_year = int(datetime.datetime.now().year)

    birth_year = current_year - aprox_age
    birth_month = random.randint(1,12)
    birth_day = random.randint(1,28)

    dob = datetime.date(birth_year, birth_month, birth_day)

    return dob


def generate_city():
    pass

def generate_zip():
    pass