# (c) 2014 Amplify Education, Inc. All rights reserved, subject to the license
# below.
#
# Education agencies that are members of the Smarter Balanced Assessment
# Consortium as of August 1, 2014 are granted a worldwide, non-exclusive, fully
# paid-up, royalty-free, perpetual license, to access, use, execute, reproduce,
# display, distribute, perform and create derivative works of the software
# included in the Reporting Platform, including the source code to such software.
# This license includes the right to grant sublicenses by such consortium members
# to third party vendors solely for the purpose of performing services on behalf
# of such consortium member educational agencies.

import os
from edcore.utils.utils import xml_datetime_convert


def generate_path_to_raw_xml(root_dir, extension='xml', **kwargs):
    """Generates file path for raw xml extract.
    """
    return generate_file_path(root_dir, extension=extension, **kwargs)


def generate_path_to_item_csv(items_root_dir, extension='csv', **kwargs):
    """Generates file path for item level csv data.
    """
    return generate_file_path(items_root_dir, extension=extension, **kwargs)


def generate_file_path(items_root_dir, extension=None, state_code=None, asmt_year=None,
                       asmt_type=None, effective_date=None, asmt_subject=None,
                       asmt_grade=None, district_id=None, student_id=None, **kwargs):
    """Generates a directory path or a file path with file extension.

    Return value has below format:

    items_root_dir/<state_code>/<asmt_year>/<asmt_type>/[effective_date]/<asmt_subject>/<asmt_grade>/<district_id>/<student_id>.extension

    A whole file path is generated if all named parameters except
    effective_date have a not None value. If effective_date is None,
    this function will skip it and continue generating path for the
    rest, whereas if any other parameters have a value of None, this
    function will return currently generated path immediately, which
    is a path to a directory.

    """
    def path_with_extention(path):
        return (path + '.' + extension) if extension is not None else path

    if type(asmt_year) is int:
        asmt_year = str(asmt_year)
    if type(effective_date) is int:
        effective_date = str(effective_date)
    effective_date = xml_datetime_convert(effective_date)
    if type(asmt_grade) is int:
        asmt_grade = str(asmt_grade)
    path = items_root_dir
    if state_code is not None:
        path = os.path.join(path, state_code.upper())
    else:
        return path_with_extention(path)
    if asmt_year is not None:
        path = os.path.join(path, asmt_year)
    else:
        return path_with_extention(path)
    if asmt_type is not None:
        path = os.path.join(path, asmt_type.upper().replace(' ', '_'))
    else:
        return path_with_extention(path)
    if effective_date is not None:
        path = os.path.join(path, effective_date)
    if asmt_subject is not None:
        path = os.path.join(path, asmt_subject.upper())
    else:
        return path_with_extention(path)
    if asmt_grade is not None:
        path = os.path.join(path, asmt_grade)
    else:
        return path_with_extention(path)
    if district_id is not None:
        path = os.path.join(path, district_id)
    else:
        return path_with_extention(path)
    if student_id is not None:
        path = os.path.join(path, student_id)
    return path_with_extention(path)
