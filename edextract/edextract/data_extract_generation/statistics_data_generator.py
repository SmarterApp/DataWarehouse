__author__ = 'ablum'


def generate_data_row(current_year_count, previous_year_count, current_year_total, previous_year_total):
    '''
    Generates a data row with statistics
    @param current_year_count: The count of a certain demographic for the current year
    @param previous_year_count: The count of a certain demographic for the previous year
    @param current_year_total: The total for the current year
    @param previous_year_total: The total for the previous year
    @return: A data row including all statistics
    '''

    percent_of_prev_year_total = _percentage(previous_year_count, previous_year_total)
    percent_of_current_year_total = _percentage(current_year_count, current_year_total)

    change_in_count = _subtract(current_year_count, previous_year_count)
    percent_difference_of_count = _percentage(change_in_count, previous_year_count)

    change_in_percentage_of_total = percent_of_current_year_total - percent_of_prev_year_total \
        if percent_of_current_year_total is not None and percent_of_prev_year_total is not None else None

    return [previous_year_count, percent_of_prev_year_total,
            current_year_count, percent_of_current_year_total,
            change_in_count, percent_difference_of_count, change_in_percentage_of_total]


def _percentage(count, total):
    if total:
        return round((count / total) * 100, 2)
    else:
        return None


def _subtract(int1, int2):
    if int1 is not None and int2 is not None:
        return int1 - int2
    else:
        return None
