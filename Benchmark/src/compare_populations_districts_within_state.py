'''
Created on Feb 15, 2013

@author: Smitha Pitla, swimberly

Districts withing a state query

Public interface:
state_statistics(state_id, connection, schema_name)
districts_in_a_state(state_id, asmt_type, asmt_subject, connection, schema_name)

Descriptions:
'state_statistics()' prints statistics for how long it takes for the query to return
for each of the different types of queries:
Summative-ELA, Summative-Math, Interim-ELA, Interim-Math

'districts_in_a_state()': returns the result of running the query on the
given parameters
'''

import time


def state_statistics(state_id, connection, schema_name):
    '''
    Runs queries that print out the statistics and benchmarks for a state
    INPUT:
    state_id -- an id for a state from the database
    connection -- the db connection created by a sqlAlchemy connect() statement
    schema_name -- the name of the schema to use in the queries
    RETURNS:
    result_dict -- A dictionary of results. The dictionary will have two items: 'stats' and 'benchmarks'
        'stats' is a dictionary of two items a float and a list of dicts 'query_time' and 'data' respectively.
            'data' is a list of query results in a dict with keys: name and value
        'descriptor' is the string 'State' to help identify the result
        'id' is the id that was used for the query
        'benchmarks' is a dictionary of 'total_time', 'total_rows' and 'data'. 'data' is a list of dictionaries.
            Each dictionary in 'data' has keys: 'type', 'query_time' and 'result'
    '''

    result_dict = {}

    if state_id is None or connection is None:
        raise ValueError('Bad Params for state_id or connection')

    district_count_query = '''
    select count(*)
    from {schema}.dim_district district
    where district.state_id = '{state_id}'
    '''.format(state_id=state_id, schema=schema_name)

    student_count_query = '''
    select count(*)
    from {schema}.dim_student student
    where student.state_id = '{state_id}'
    '''.format(state_id=state_id, schema=schema_name)

    # Execute Queries
    start_time = time.time()
    school_count_set = connection.execute(district_count_query).fetchall()[0][0]
    stu_count_set = connection.execute(student_count_query).fetchall()[0][0]
    query_time = time.time() - start_time

    result_dict['stats'] = {'query_time': query_time, 'data': []}

    result_dict['descriptor'] = 'State'
    result_dict['id'] = state_id

    result_dict['stats']['data'].append({'name': 'Schools in State', 'value': school_count_set})
    result_dict['stats']['data'].append({'name': 'Students in State', 'value': stu_count_set})

    result_dict['benchmarks'] = {'total_time': 0, 'total_rows': 0, 'data': []}

    # Run Queries for each of the 4 types of assessments
    start_time1 = time.time()
    res = districts_in_a_state(state_id, 'SUMMATIVE', 'ELA', connection, schema_name)
    query_time = time.time() - start_time1
    result_dict['benchmarks']['data'].append({'type': 'Summative-ELA', 'query_time': query_time, 'result': res})
    result_dict['benchmarks']['total_time'] += query_time
    result_dict['benchmarks']['total_rows'] += len(res)

    start_time1 = time.time()
    res = districts_in_a_state(state_id, 'INTERIM', 'ELA', connection, schema_name)
    query_time = time.time() - start_time1
    result_dict['benchmarks']['data'].append({'type': 'Interim-ELA', 'query_time': query_time, 'result': res})
    result_dict['benchmarks']['total_time'] += query_time
    result_dict['benchmarks']['total_rows'] += len(res)

    start_time1 = time.time()
    districts_in_a_state(state_id, 'SUMMATIVE', 'Math', connection, schema_name)
    query_time = time.time() - start_time1
    result_dict['benchmarks']['data'].append({'type': 'Summative-Math', 'query_time': query_time, 'result': res})
    result_dict['benchmarks']['total_time'] += query_time
    result_dict['benchmarks']['total_rows'] += len(res)

    start_time1 = time.time()
    districts_in_a_state(state_id, 'INTERIM', 'Math', connection, schema_name)
    query_time = time.time() - start_time1
    result_dict['benchmarks']['data'].append({'type': 'Interim-Math', 'query_time': query_time, 'result': res})
    result_dict['benchmarks']['total_time'] += query_time
    result_dict['benchmarks']['total_rows'] += len(res)

    return result_dict


def districts_in_a_state(state_id, asmt_type, asmt_subject, connection, schema_name):
    '''
    Run a query for assessment performance for districts within a state.
    INPUT:
    state_id -- the id of the state that you want to use in the query (ie. 'DE' for deleware)
    asmt_type -- the type of assessment to use in the query ('SUMMATIVE' or 'INTERIM')
    asmt_subject -- the subject of assessment to use in the query ('ELA' or 'Math')
    connection -- the db connection created by a sqlAlchemy connect() statement
    schema_name -- the name of the schema to use in the queries
    RETURNS: result -- a list of tuples (district, count, performance level)
    '''

    query = """
    select dist.district_name, count(fact.student_id),
    case when fact.asmt_score <= asmt.asmt_cut_point_1 then asmt.asmt_perf_lvl_name_1
    when fact.asmt_score > asmt.asmt_cut_point_1 and fact.asmt_score <= asmt.asmt_cut_point_2 then asmt.asmt_perf_lvl_name_2
    when fact.asmt_score > asmt.asmt_cut_point_2 and fact.asmt_score <= asmt.asmt_cut_point_3 then asmt.asmt_perf_lvl_name_3
    when fact.asmt_score > asmt.asmt_cut_point_3  then asmt.asmt_perf_lvl_name_4
    end
    as performance_level
    from
    {schema}.dim_asmt asmt,
    {schema}.dim_district dist,
    {schema}.fact_asmt_outcome fact,
    {schema}.dim_student stu
    where asmt.asmt_id = fact.asmt_id
    and dist.district_id = fact.district_id
    and stu.student_id = fact.student_id
    and fact.date_taken_year='2012'
    and fact.state_id = '{state_id}'
    and asmt.asmt_type = '{asmt_type}'
    and asmt.asmt_subject = '{asmt_subject}'
    group by dist.district_name, performance_level
    """.format(state_id=state_id, asmt_type=asmt_type, asmt_subject=asmt_subject, schema=schema_name)

    resultset = connection.execute(query)
    results = resultset.fetchall()

    return results

if __name__ == '__main__':
#    #engine = create_engine('postgresql+psycopg2://postgres:postgres@monetdb1.poc.dum.edwdc.net:5432/edware')
#    engine = create_engine('postgresql+psycopg2://postgres:edware2013@edwdbsrv2.poc.dum.edwdc.net:5432/edware')
#    #schema_name = 'edware_star_20130212_fixture_3'
#    schema_name = 'edware_star_20130215_2'
#    connection = engine.connect()

    print("This module is not runnable from the command line. For usage instructions:")
    print("python benchmark.py -h")
