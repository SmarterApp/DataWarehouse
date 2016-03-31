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
Created on Jan 13, 2013
'''
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import label, case
from smarter.reports.helpers.constants import Constants, AssessmentType
from edapi.cache import cache_region
from sqlalchemy.sql.functions import count
from edcore.database.edcore_connector import EdCoreDBConnection

BUCKET_SIZE = 20


@cache_region('public.data')
def get_summary_distribution(state_code, district_id=None, school_id=None, asmt_type=AssessmentType.SUMMATIVE):
    '''
    Get a bucketed distribution of scores
    '''
    with EdCoreDBConnection(state_code=state_code) as connection:
        fact_asmt_outcome_vw = connection.get_table('fact_asmt_outcome')
        #  should it be always for summative?
        query = select([label(Constants.SCORE_BUCKET, (fact_asmt_outcome_vw.c.asmt_score / get_bucket_size()) * get_bucket_size()),
                        count(case([(fact_asmt_outcome_vw.c.asmt_subject == Constants.MATH, 1)], else_=0)).label(Constants.TOTAL_MATH),
                        count(case([(fact_asmt_outcome_vw.c.asmt_subject == Constants.ELA, 1)], else_=0)).label(Constants.TOTAL_ELA)],
                       from_obj=[fact_asmt_outcome_vw])
        query = query.where(fact_asmt_outcome_vw.c.state_code == state_code)
        query = query.where(fact_asmt_outcome_vw.c.asmt_type == asmt_type)
        query = query.where(fact_asmt_outcome_vw.c.rec_status == Constants.CURRENT)
        if (district_id is not None):
            query = query.where(fact_asmt_outcome_vw.c.district_id == district_id)
        if (school_id is not None):
            query = query.where(fact_asmt_outcome_vw.c.school_id == school_id)
        query = query.group_by(Constants.SCORE_BUCKET).order_by(Constants.SCORE_BUCKET)
        return connection.get_result(query)


def get_bucket_size():
    return BUCKET_SIZE
