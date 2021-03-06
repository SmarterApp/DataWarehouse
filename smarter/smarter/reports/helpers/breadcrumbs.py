# (c) 2014 The Regents of the University of California. All rights reserved,
# subject to the license below.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0. Unless required by
# applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

'''
Breadcrumbs are a front-end navigation widget to traverse up
and down the report hierarchy. They are displayed at the top
of each report.

Created on Mar 8, 2013

@author: dip
'''
from sqlalchemy.sql import and_, select
from smarter.reports.helpers.constants import Constants
from edcore.database.routing import ReportingDbConnection

STATE_NAMES = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'DC': 'District of Columbia',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming'
}


def get_breadcrumbs_context(state_code=None, district_id=None, school_id=None, asmt_grade=None, student_name=None, tenant=None, is_public=False):
    '''
    Given certain known information, returns breadcrumbs context
    It'll always return "home" breadcrumbs into results
    '''
    formatted_results = [{'type': 'home', 'name': 'Home'}]
    results = None
    if state_code:
        with ReportingDbConnection(tenant=tenant, state_code=state_code, is_public=is_public) as connector:
            dim_inst_hier = connector.get_table('dim_inst_hier')
            # Limit result count to one
            # We limit the results to one since we'll get multiple rows with the same values
            # Think of the case of querying for state name and id, we'll get all the schools in that state
            query = select([dim_inst_hier.c.state_code.label(Constants.STATE_CODE),
                            dim_inst_hier.c.district_name.label(Constants.DISTRICT_NAME),
                            dim_inst_hier.c.school_name.label(Constants.SCHOOL_NAME)],
                           from_obj=[dim_inst_hier], limit=1)

            query = query.where(and_(dim_inst_hier.c.rec_status == Constants.CURRENT))
            # Currently, we only have state_id from comparing population report
            if state_code is not None:
                query = query.where(and_(dim_inst_hier.c.state_code == state_code))
            if district_id is not None:
                query = query.where(and_(dim_inst_hier.c.district_id == district_id))
                if school_id is not None:
                    query = query.where(and_(dim_inst_hier.c.school_id == school_id))

            # run it and format the results
            results = connector.get_result(query)
    if results:
        result = results[0]
        # return an hierarchical ordered list
        formatted_results.append({'type': 'state', 'name': STATE_NAMES.get(result[Constants.STATE_CODE], 'Example State'), 'stateCode': result[Constants.STATE_CODE], 'id': result[Constants.STATE_CODE]})
        if district_id is not None:
            formatted_results.append({'type': 'district', 'name': result[Constants.DISTRICT_NAME], 'id': district_id})
            if school_id is not None:
                formatted_results.append({'type': 'school', 'name': result[Constants.SCHOOL_NAME], 'id': school_id})
                if asmt_grade is not None:
                    formatted_results.append({'type': 'grade', 'name': asmt_grade, 'id': asmt_grade})
                    if student_name is not None:
                        formatted_results.append({'type': 'student', 'name': student_name})

    return {'items': formatted_results}
