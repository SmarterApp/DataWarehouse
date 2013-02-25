'''
Created on Feb 15, 2013

@author: Smitha Pitla, swimberly

schools withing a district query

Public interface:
district_statistics(state_id, connection)
schools_in_a_district(state_id, asmt_type, asmt_subject, connection)

Descriptions:
'district_statistics()' prints statistics for how long it takes for the query to return
for each of the different types of queries:
Summative-ELA, Summative-Math, Interim-ELA, Interim-Math

'schools_in_a_district()': returns the result of running the query on the
given parameters
'''

import time

from sqlalchemy import create_engine


def district_statistics(district_id, connection, schema_name):
    '''
    Runs queries that print out the statistics and benchmarks for a district
    INPUT:
    state_id -- an id for a state from the database
    connection -- the db connection created by a sqlAlchemy connection() statement
    schema_name -- the name of the schema to use in the queries
    RETURNS:
    result_dict -- A dictionary of results. The dictionary will have two items: 'stats' and 'benchmarks'
        'stats' is a dictionary of two items a float and a list of dicts 'query_time' and 'data' respectively.
            'data' is a list of query results in a (name, value) tuple
        'benchmarks' is a list of dictionaries. Each dictionary has keys: 'type', 'query_time' and 'result'
    '''

    result_dict = {}

    school_count_query = '''
    select count(*)
    from {schema}.dim_school school
    where school.district_id = {district_id}
    '''.format(district_id=district_id, schema=schema_name)

    student_count_query = '''
    select count(*)
    from {schema}.dim_student student
    where student.district_id = {district_id}
    '''.format(district_id=district_id, schema=schema_name)

    total_students_query = '''
    select count(*)
    from {schema}.dim_student
    '''.format(schema=schema_name)

    total_dist_query = '''
    select count(*)
    from {schema}.dim_district
    '''.format(schema=schema_name)

    total_schools_query = '''
    select count(*)
    from {schema}.dim_school
    '''.format(schema=schema_name)

    start_time = time.time()
    school_count_set = connection.execute(school_count_query).fetchall()[0][0]
    stu_count_set = connection.execute(student_count_query).fetchall()[0][0]
    tot_stu_set = connection.execute(total_students_query).fetchall()[0][0]
    tot_dist_set = connection.execute(total_dist_query).fetchall()[0][0]
    tot_sch_set = connection.execute(total_schools_query).fetchall()[0][0]
    query_time = time.time() - start_time

    result_dict['stats'] = {'query_time': query_time, 'data': []}

    result_dict['stats']['data'].append(('Total Districts', tot_dist_set))
    result_dict['stats']['data'].append(('Total Schools', tot_sch_set))
    result_dict['stats']['data'].append(('Total Students', tot_stu_set))
    result_dict['stats']['data'].append(('Schools in District', school_count_set))
    result_dict['stats']['data'].append(('Students in District', stu_count_set))

    print('************* Benchmarks for District %d *************' % district_id)
    print('Total Districts:\t%6d' % tot_dist_set)
    print('Total Schools:\t\t%6d' % tot_sch_set)
    print('Total Students:\t\t%6d' % tot_stu_set)
    print('Schools in district:\t%6d' % school_count_set)
    print('Students in district:\t%6d' % stu_count_set)
    print('Time to run counts:\t%6.3fs' % query_time)
    print('**** Benchmarks for Queries ****')

    result_dict['benchmarks'] = []

    start_time1 = time.time()
    res = schools_in_a_district(district_id, 'SUMMATIVE', 'ELA', connection, schema_name)
    query_time = time.time() - start_time1
    print('Summative-ELA:\t\t%6.2fs' % query_time)
    result_dict['benchmarks'].append({'type': 'Summative-ELA', 'query_time': query_time, 'result': res})

    start_time1 = time.time()
    res = schools_in_a_district(district_id, 'INTERIM', 'ELA', connection, schema_name)
    query_time = time.time() - start_time1
    print('Interim-ELA:\t\t%6.2fs' % query_time)
    result_dict['benchmarks'].append({'type': 'Interim-ELA', 'query_time': query_time, 'result': res})

    start_time1 = time.time()
    res = schools_in_a_district(district_id, 'SUMMATIVE', 'Math', connection, schema_name)
    query_time = time.time() - start_time1
    print('Summative-Math:\t\t%6.2fs' % query_time)
    result_dict['benchmarks'].append({'type': 'Summative-Math', 'query_time': query_time, 'result': res})

    start_time1 = time.time()
    res = schools_in_a_district(district_id, 'INTERIM', 'Math', connection, schema_name)
    query_time = time.time() - start_time1
    print('Interim-Math:\t\t%6.2fs' % query_time)
    result_dict['benchmarks'].append({'type': 'Interim-Math', 'query_time': query_time, 'result': res})

    return result_dict


def schools_in_a_district(district_id, asmt_type, asmt_subject, connection, schema_name):
    '''
    Run a query for assessment performance for grades within a school.
    INPUT:
    state_id -- the id of the state that you want to use in the query (ie. 'DE' for deleware)
    asmt_type -- the type of assessment to use in the query ('SUMMATIVE' or 'INTERIM')
    asmt_subject -- the subject of assessment to use in the query ('ELA' or 'Math')
    connection -- the db connection created by a sqlAlchemy connection() statement
    schema_name -- the name of the schema to use in the queries
    RETURNS: results -- a list of tuples (school, count, performance level)
    '''

    query = """
    select school.school_name, count(fact.student_id),
    case
    when fact.asmt_score <= asmt.asmt_cut_point_1 then asmt.asmt_perf_lvl_name_1
    when fact.asmt_score > asmt.asmt_cut_point_1 and fact.asmt_score <= asmt.asmt_cut_point_2 then asmt.asmt_perf_lvl_name_2
    when fact.asmt_score > asmt.asmt_cut_point_2 and fact.asmt_score <= asmt.asmt_cut_point_3 then asmt.asmt_perf_lvl_name_3
    when fact.asmt_score > asmt.asmt_cut_point_3  then asmt.asmt_perf_lvl_name_4
    end
    as performance_level
    from
    {schema}.dim_asmt asmt,
    {schema}.dim_school school,
    {schema}.fact_asmt_outcome fact,
    {schema}.dim_student stu
    where asmt.asmt_id = fact.asmt_id
    and school.school_id = fact.school_id
    and stu.student_id = fact.student_id
    and fact.date_taken_year='2012'
    and fact.district_id = {district_id}
    and asmt.asmt_type = '{asmt_type}'
    and asmt.asmt_subject = '{asmt_subject}'
    group by school.school_name, performance_level
    """.format(district_id=district_id, asmt_type=asmt_type, asmt_subject=asmt_subject, schema=schema_name)
    #print(district)
    resultset = connection.execute(query)
    results = resultset.fetchall()
    #print(results)
    return results


if __name__ == '__main__':
    import time

    engine = create_engine('postgresql://postgres:postgres@monetdb1.poc.dum.edwdc.net:5432/edware')
    schema_name = 'edware_star_20130212_fixture_3'
    connection = engine.connect()

    district_statistics(161, connection, schema_name)
    district_statistics(127, connection, schema_name)
    district_statistics(143, connection, schema_name)

    stime = time.time()
    result = schools_in_a_district(161, 'SUMMATIVE', 'ELA', connection, schema_name)
    duration = time.time() - stime
    result.sort(key=lambda tup: tup[0])

    for res in result:
        print(res)
