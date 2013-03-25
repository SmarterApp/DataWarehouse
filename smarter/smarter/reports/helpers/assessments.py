'''
Created on Mar 20, 2013

@author: dip
'''
import json


def get_overall_asmt_interval(result):
    '''
    Given a dictionary, return overall assessment interval
    Logic is to interval is the difference of score and min score range
    '''
    return result['asmt_score'] - result['asmt_score_range_min']


def get_cut_points(result):
    '''
    Given a dictionary, return a formatted results for assessment cutpoints and colors
    '''
    result['cut_point_intervals'] = []

    custom_metadata = result['asmt_custom_metadata']
    custom = None if not custom_metadata else json.loads(custom_metadata)
    # once we use the data, we clean it from the result
    del(result['asmt_custom_metadata'])

    # go over the 4 cut points
    for i in range(1, 5):
        # we only take cutpoints with values > 0
        cut_point_interval = result['asmt_cut_point_{0}'.format(i)]
        # if it's the forth interval, we would have a value anyway.
        if i == 4 or (cut_point_interval and cut_point_interval > 0):
            cut_point_interval_object = {'name': str(result['asmt_cut_point_name_{0}'.format(i)]),
                                         'interval': str(cut_point_interval)}

            # the value of the 4th interval is the assessment max score
            if (i == 4):
                cut_point_interval_object['interval'] = str(result['asmt_score_max'])
            # once we use the data, we clean it from the result
            del(result['asmt_cut_point_name_{0}'.format(i)])
            del(result['asmt_cut_point_{0}'.format(i)])
            # connect the custom metadata content to the cut_point_interval object
            if custom is not None:
                result['cut_point_intervals'].append(dict(list(cut_point_interval_object.items()) + list(custom[i - 1].items())))
            else:
                result['cut_point_intervals'].append(cut_point_interval_object)

    # remove unnecessary cut point name
    if 'asmt_cut_point_name_5' in result:
        del(result['asmt_cut_point_name_5'])
    return result


def get_claims(number_of_claims=0, result=None, get_names_only=False):
    '''
    Returns a list of claims information
    if get_name_only is True, it returns only the name of the claim and its equivalence claim number name
    '''
    claims = []
    for index in range(1, number_of_claims + 1):
        claim_name = result.get('asmt_claim_{0}_name'.format(index))
        if claim_name is not None and len(claim_name) > 0:
            claim_score = result.get('asmt_claim_{0}_score'.format(index))
            claim_object = {'name': claim_name,
                            'name2': 'Claim ' + str(index)}
            if not get_names_only:
                claim_object['score'] = str(claim_score)
                claim_object['indexer'] = str(index),
                claim_object['range_min_score'] = str(result.get('asmt_claim_{0}_score_range_min'.format(index)))
                claim_object['range_max_score'] = str(result.get('asmt_claim_{0}_score_range_max'.format(index)))
                claim_object['max_score'] = str(result.get('asmt_claim_{0}_score_max'.format(index)))
                claim_object['min_score'] = str(result.get('asmt_claim_{0}_score_min'.format(index)))
                claim_object['confidence'] = str(claim_score - result.get('asmt_claim_{0}_score_range_min'.format(index)))

            # TODO: refactor, process by subject
            if result['asmt_subject'] == 'Math' and index == 2:
                claim_object['name2'] = 'Claim 2 & 4'

            claims.append(claim_object)

        # deleting duplicated record
        if 'asmt_claim_{0}_name'.format(index) in result:
            del(result['asmt_claim_{0}_name'.format(index)])
        if 'asmt_claim_{0}_score'.format(index) in result:
            del(result['asmt_claim_{0}_score'.format(index)])
        if 'asmt_claim_{0}_score_range_min'.format(index) in result:
            del(result['asmt_claim_{0}_score_range_min'.format(index)])
        if 'asmt_claim_{0}_score_range_max'.format(index) in result:
            del(result['asmt_claim_{0}_score_range_max'.format(index)])
        if 'asmt_claim_{0}_score_min'.format(index) in result:
            del(result['asmt_claim_{0}_score_min'.format(index)])
        if 'asmt_claim_{0}_score_max'.format(index) in result:
            del(result['asmt_claim_{0}_score_max'.format(index)])
    return claims
