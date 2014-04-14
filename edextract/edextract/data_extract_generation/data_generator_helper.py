__author__ = 'tshewchuk'


"""
This module contains utility functions used in report data generation.
"""


def percentage(count, total):
    """
    Safe percentage calculating function.

    @param count: Count for some category for the year
    @param total: Total for the year

    @return: Adjusted percentage of count to total (int or None)
    """

    if count is not None and total:
        return (count / total) * 100
    else:
        return None


def subtract(subtractor, subtractee):
    """
    Safe subtraction calculating function.

    @param subtractor: Number from which to subtract subtractee
    @param subtractee: Number which to subtract from subtractor

    @return: Adjusted subtraction of subtractee from subtractor (int or None)
    """

    if subtractor is not None and subtractee is not None:
        return subtractor - subtractee
    else:
        return None


def format_floatval(floatval):
    """
    Convert floating point value to formatted string for report.

    @param floatval: Floating point value

    @return: Formatted string representation of floating point value
    """
    if floatval is not None:
        return str(round(floatval, 2)).rstrip('0').rstrip('.')
    else:
        return ''


def format_intval(intval):
    """
    Convert integer value to formatted string for report.

    @param intval: Integer value

    @return: Formatted string representation of integer value
    """
    if intval is not None:
        return str(intval)
    else:
        return ''
