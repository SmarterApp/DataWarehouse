'''
Created on Feb 25, 2013

@author: dip
'''


# converts a string value to int, returns None if value is None
def convert_to_int(value):
    converted_value = None
    if value is not None:
        try:
            converted_value = int(value)
        except ValueError:
            return None
    return converted_value


# boolean True/False converter
def to_bool(val):
    return val and val.lower() in ('true', 'True')


# enum
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.items())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)
