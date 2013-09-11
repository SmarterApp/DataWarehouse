'''
Created on Mar 7, 2013

@author: dwu
'''

from edapi.decorators import report_config, user_info
from smarter.reports.helpers.percentage_calc import normalize_percentages
from sqlalchemy.sql import select
from sqlalchemy.sql import and_
from smarter.reports.helpers.breadcrumbs import get_breadcrumbs_context
from sqlalchemy.sql.expression import func, true
from smarter.reports.helpers.constants import Constants
from edapi.logging import audit_event
import collections
from edapi.exceptions import NotFoundException
from smarter.security.context import select_with_context
from smarter.database.smarter_connector import SmarterDBConnection
from smarter.reports.exceptions.parameter_exception import InvalidParameterException
from smarter.reports.helpers.metadata import get_custom_metadata
from edapi.cache import cache_region
from smarter.reports.filters.demographics import apply_demographics_filter_to_query,\
    DEMOGRAPHICS_CONFIG
from smarter.reports.helpers.utils import merge_dict


REPORT_NAME = "comparing_populations"
CACHE_REGION_PUBLIC_DATA = 'public.data'
CACHE_REGION_PUBLIC_FILTERING_DATA = 'public.filtered_data'
DEFAULT_MIN_CELL_SIZE = 0


@report_config(
    name=REPORT_NAME,
    params=merge_dict({
        Constants.STATECODE: {
            "type": "string",
            "required": True,
            "pattern": "^[a-zA-Z]{2}$",
        },
        Constants.DISTRICTGUID: {
            "type": "string",
            "required": False,
            "pattern": "^[a-zA-Z0-9\-]{0,50}$",
        },
        Constants.SCHOOLGUID: {
            "type": "string",
            "required": False,
            "pattern": "^[a-zA-Z0-9\-]{0,50}$",
        }
    }, DEMOGRAPHICS_CONFIG))
@audit_event()
@user_info
def get_comparing_populations_report(params):
    '''
    Comparing Populations Report
    '''
    noFilters = _is_filtering(params)
    if noFilters:
        return get_unfiltered_report(params)  
    else:
        return get_filtered_report(params)

def _is_filtering(params):
    '''
    Return true if no demographics parameter
    '''
    return params.keys().isdisjoint(DEMOGRAPHICS_CONFIG.keys())

def get_filtered_report(params):
    '''
    Comparing Populations Report with filters
    '''    
    filtered = ComparingPopReport(**params).get_report()
    unfiltered = get_unfiltered_report(params)
    return merge_results(filtered, unfiltered)

def get_unfiltered_report(params):
    '''
    Comparing Populations Report without filters
    '''
    params = { k: v for k, v in params.items() if k not in DEMOGRAPHICS_CONFIG }
    return ComparingPopReport(**params).get_report()

def merge_results(filtered, unfiltered):
    '''
    Merge unfiltered count to filtered results
    '''
    cache = { record['id']: record['results'] for record in unfiltered['records'] }
    for subject in filtered['subjects']:
        # merge summary
        filtered['summary'][0]['results'][subject]['unfilteredTotal'] = unfiltered['summary'][0]['results'][subject]['total'] 
        # merge each record
        for record in filtered['records']:
            total = cache[record['id']][subject]['total']
            record['results'][subject]['unfilteredTotal'] = total
    return filtered

def get_comparing_populations_cache_route(comparing_pop):
    '''
    Returns cache region based on whether filters exist
    If school_guid is present, return none - do not cache

    :param comparing_pop:  instance of ComparingPopReport
    '''
    if comparing_pop.school_guid is not None:
        return None  # do not cache school level
    return CACHE_REGION_PUBLIC_FILTERING_DATA if len(comparing_pop.filters.keys()) > 0 else CACHE_REGION_PUBLIC_DATA


def get_comparing_populations_cache_key(comparing_pop):
    '''
    Returns cache key for comparing populations report

    :param comparing_pop:  instance of ComparingPopReport
    :returns: a tuple representing a unique key for comparing populations report
    '''
    cache_args = []
    if comparing_pop.state_code is not None:
        cache_args.append(comparing_pop.state_code)
    if comparing_pop.district_guid is not None:
        cache_args.append(comparing_pop.district_guid)
    filters = comparing_pop.filters
    # sorts dictionary of keys
    cache_args.append(sorted(filters.items(), key=lambda x: x[0]))
    return tuple(cache_args)


def set_default_min_cell_size(default_min_cell_size):
    '''
    UTs ONLY!!!
    '''
    global DEFAULT_MIN_CELL_SIZE
    DEFAULT_MIN_CELL_SIZE = default_min_cell_size


class ComparingPopReport(object):
    '''
    Comparing populations report
    '''
    def __init__(self, stateCode=None, districtGuid=None, schoolGuid=None, tenant=None, **filters):
        '''
        :param string stateCode:  State code representing the state
        :param string districtGuid:  Guid of the district, could be None
        :param string schoolGuid:  Guid of the school, could be None
        :param string tenant:  tenant name of the user.  Specify if report is not going through a web request
        :param dict filter: dict of filters to apply to query
        '''
        self.state_code = stateCode
        self.district_guid = districtGuid
        self.school_guid = schoolGuid
        self.tenant = tenant
        self.filters = filters

    def set_district_guid(self, guid):
        '''
        Sets district guid

        :param string guid:  the guid to set district guid to be
        '''
        self.district_guid = guid

    def set_filters(self, filters):
        '''
        Sets the demographic filters for comparing populations

        :param dict filters:  key value pairs of demographic criteria
        '''
        self.filters = filters

    @cache_region([CACHE_REGION_PUBLIC_DATA, CACHE_REGION_PUBLIC_FILTERING_DATA], router=get_comparing_populations_cache_route, key_generator=get_comparing_populations_cache_key)
    def get_report(self):
        '''
        Actual report call

        :rtype: dict
        :returns: A comparing populations report based on parameters supplied
        '''
        params = {Constants.STATECODE: self.state_code, Constants.DISTRICTGUID: self.district_guid, Constants.SCHOOLGUID: self.school_guid, 'filters': self.filters}
        results = self.run_query(**params)

        # Only return 404 if results is empty and there are no filters being applied
        if not results and len(self.filters.keys()) is 0:
            raise NotFoundException("There are no results")

        return self.arrange_results(results, **params)

    def run_query(self, **params):
        '''
        Run comparing populations query and return the results

        :rtype: dict
        :returns:  results from database
        '''
        with SmarterDBConnection(tenant=self.tenant) as connector:
            query_helper = QueryHelper(connector, **params)
            query = query_helper.get_query()
            results = connector.get_result(query)
        return results

    def arrange_results(self, results, **param):
        '''
        Arrange the results in optimal way to be consumed by front-end

        :rtype: dict
        :returns:  results arranged for front-end consumption
        '''
        subjects = collections.OrderedDict({Constants.MATH: Constants.SUBJECT1, Constants.ELA: Constants.SUBJECT2})
        custom_metadata = get_custom_metadata(param.get(Constants.STATECODE), self.tenant)
        record_manager = RecordManager(subjects, self.get_asmt_levels(subjects, custom_metadata), custom_metadata, **param)

        for result in results:
            record_manager.update_record(result)

        # bind the results
        return {Constants.METADATA: custom_metadata,
                Constants.SUMMARY: record_manager.get_summary(), Constants.RECORDS: record_manager.get_records(),
                Constants.SUBJECTS: record_manager.get_subjects(),  # reverse map keys and values for subject
                Constants.CONTEXT: get_breadcrumbs_context(state_code=param.get(Constants.STATECODE), district_guid=param.get(Constants.DISTRICTGUID), school_guid=param.get(Constants.SCHOOLGUID), tenant=self.tenant)}

    @staticmethod
    def get_asmt_levels(subjects, metadata):
        asmt_map = {}
        for alias in subjects.values():
            asmt_map[alias] = 4
            color = metadata.get(alias, {}).get(Constants.COLORS)
            if color:
                asmt_map[alias] = len(color)
        return asmt_map


class RecordManager():
    def __init__(self, subjects_map, asmt_level, custom_metadata={}, stateCode=None, districtGuid=None, schoolGuid=None, **kwargs):
        self._stateCode = stateCode
        self._districtGuid = districtGuid
        self._schoolGuid = schoolGuid
        self._subjects_map = subjects_map
        self._tracking_record = collections.OrderedDict()
        self._summary = {}
        self._custom_metadata = custom_metadata
        self._asmt_level = asmt_level
        self.init_summary(self._summary)

    def init_summary(self, data):
        if self._subjects_map is not None:
            for alias in self._subjects_map.values():
                data[alias] = {}

    def update_record(self, result):
        '''
        add a result set to manager, and store by the name of subjects
        '''
        inst_id = result[Constants.ID]
        record = self._tracking_record.get(inst_id, None)
        subject_alias_name = self._subjects_map[result[Constants.ASMT_SUBJECT]]
        # otherwise, create new empty record
        if record is None:
            record = Record(inst_id=inst_id, name=result[Constants.NAME])
            self._tracking_record[inst_id] = record
            self.init_summary(record.subjects)

        # Update overall summary and summary for current record
        self.update_interval(self._summary[subject_alias_name], result[Constants.LEVEL], result[Constants.TOTAL])
        self.update_interval(record.subjects[subject_alias_name], result[Constants.LEVEL], result[Constants.TOTAL])

    def update_interval(self, data, level, count):
        data[level] = data.get(level, 0) + int(count)

    def get_subjects(self):
        '''
        reverse subjects map for FE
        '''
        return {v: k for k, v in self._subjects_map.items()}

    def get_summary(self):
        return [{Constants.RESULTS: self.format_results(self._summary)}]

    def format_results(self, data):
        '''
        return summary of all records
        '''
        results = collections.OrderedDict()

        if self._subjects_map is not None:
            for name, alias in self._subjects_map.items():
                levels = self._asmt_level.get(alias)
                if levels and levels != len(data[alias]):
                    for index in range(1, levels + 1):
                        if data[alias].get(index) is None:
                            data[alias][index] = 0
                intervals = []
                total = 0
                for level, count in data[alias].items():
                    total += count
                    intervals.append({Constants.LEVEL: level, Constants.COUNT: count})
                for interval in intervals:
                    interval[Constants.PERCENTAGE] = self.calculate_percentage(interval[Constants.COUNT], total)
                # adjust for min cell size policy and do not return data if violated
                if total > self._custom_metadata.get(alias, {}).get(Constants.MIN_CELL_SIZE, DEFAULT_MIN_CELL_SIZE):
                    results[alias] = {Constants.ASMT_SUBJECT: name, Constants.INTERVALS: self.adjust_percentages(intervals), Constants.TOTAL: total}
                else:
                    results[alias] = {Constants.ASMT_SUBJECT: name, Constants.INTERVALS: [{Constants.PERCENTAGE: -1} for _ in range(0, len(intervals))], Constants.TOTAL: -1}

        return results

    def get_records(self):
        '''
        return record in array and ordered by name
        '''
        records = []
        for record in self._tracking_record.values():
            __record = {Constants.ID: record.id, Constants.NAME: record.name, Constants.RESULTS: self.format_results(record.subjects), Constants.PARAMS: {Constants.STATECODE: self._stateCode, Constants.ID: record.id}}
            if self._districtGuid is not None:
                __record[Constants.PARAMS][Constants.DISTRICTGUID] = self._districtGuid
            if self._schoolGuid is not None:
                __record[Constants.PARAMS][Constants.SCHOOLGUID] = self._schoolGuid
            records.append(__record)
        return records

    @staticmethod
    def calculate_percentage(count, total):
        '''
        calculate percentage
        '''
        return 0 if total == 0 else count / total * 100

    @staticmethod
    def adjust_percentages(intervals):
        '''
        normalize interval percentages to always add up to 100
        '''
        # do the normalization
        percentages = normalize_percentages([interval[Constants.PERCENTAGE] for interval in intervals])
        newIntervals = intervals.copy()
        # set percentages back in intervals
        for idx, val in enumerate(percentages):
            newIntervals[idx][Constants.PERCENTAGE] = val
        return newIntervals


class Record():
    def __init__(self, inst_id=None, name=None):
        self._id = inst_id
        self._name = name
        self._subjects = {}

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def subjects(self):
        return self._subjects

    @subjects.setter
    def subjects(self, value):
        self._subjects = value


def enum(**enums):
    return type('Enum', (), enums)


class QueryHelper():
    '''
    Helper class to build a sqlalchemy query based on the view type (state, district, or school)
    '''
    def __init__(self, connector, stateCode=None, districtGuid=None, schoolGuid=None, filters=None):
        self._state_code = stateCode
        self._district_guid = districtGuid
        self._school_guid = schoolGuid
        self._filters = filters
        if self._state_code is not None and self._district_guid is None and self._school_guid is None:
            self._f = self.get_query_for_state_view
        elif self._state_code is not None and self._district_guid is not None and self._school_guid is None:
            self._f = self.get_query_for_district_view
        elif self._state_code is not None and self._district_guid is not None and self._school_guid is not None:
            self._f = self.get_query_for_school_view
        else:
            raise InvalidParameterException()
        self._dim_inst_hier = connector.get_table(Constants.DIM_INST_HIER)
        self._fact_asmt_outcome = connector.get_table(Constants.FACT_ASMT_OUTCOME)

    def build_query(self, f, extra_columns):
        '''
        build select columns based on request
        '''
        query = f(extra_columns +
                  [self._fact_asmt_outcome.c.asmt_subject.label(Constants.ASMT_SUBJECT),
                   self._fact_asmt_outcome.c.asmt_perf_lvl.label(Constants.LEVEL),
                   func.count().label(Constants.TOTAL)],
                  from_obj=[self._fact_asmt_outcome.join(self._dim_inst_hier, and_(self._dim_inst_hier.c.inst_hier_rec_id == self._fact_asmt_outcome.c.inst_hier_rec_id))]
                  )\
            .group_by(self._fact_asmt_outcome.c.asmt_subject,
                      self._fact_asmt_outcome.c.asmt_perf_lvl)\
            .where(and_(self._fact_asmt_outcome.c.state_code == self._state_code, self._fact_asmt_outcome.c.most_recent == true(), self._fact_asmt_outcome.c.asmt_type == Constants.SUMMATIVE))

        # apply demographics filters to query
        return apply_demographics_filter_to_query(query, self._fact_asmt_outcome, self._filters)

    def build_query_for_inst_name(self, f, inner_query, extra_columns=[]):
        '''
        Builds inner_query to get the name of district or schools
        '''
        inner_query = inner_query.alias()
        return f(extra_columns +
                 [inner_query.c[Constants.ASMT_SUBJECT], inner_query.c[Constants.LEVEL], func.sum(inner_query.c[Constants.TOTAL]).label(Constants.TOTAL)],
                 from_obj=[self._dim_inst_hier.join(inner_query, self._dim_inst_hier.c.inst_hier_rec_id == inner_query.c[Constants.INST_HIER_REC_ID])])\
            .group_by(inner_query.c[Constants.ASMT_SUBJECT], inner_query.c[Constants.LEVEL])\
            .order_by(inner_query.c[Constants.ASMT_SUBJECT].desc())

    def get_query(self):
        return self._f()

    def get_query_for_state_view(self):
        f = select
        inner_query = self.build_query(f, [self._dim_inst_hier.c.inst_hier_rec_id.label(Constants.INST_HIER_REC_ID)])\
                          .group_by(self._dim_inst_hier.c.inst_hier_rec_id)

        return self.build_query_for_inst_name(f, inner_query, [self._dim_inst_hier.c.district_name.label(Constants.NAME), self._dim_inst_hier.c.district_guid.label(Constants.ID)])\
                   .group_by(self._dim_inst_hier.c.district_name, self._dim_inst_hier.c.district_guid)\
                   .order_by(self._dim_inst_hier.c.district_name)

    def get_query_for_district_view(self):
        f = select
        inner_query = self.build_query(f, [self._dim_inst_hier.c.inst_hier_rec_id.label(Constants.INST_HIER_REC_ID)])\
                          .group_by(self._dim_inst_hier.c.inst_hier_rec_id)\
                          .where(self._fact_asmt_outcome.c.district_guid == self._district_guid)

        return self.build_query_for_inst_name(f, inner_query, [self._dim_inst_hier.c.school_name.label(Constants.NAME), self._dim_inst_hier.c.school_guid.label(Constants.ID)])\
                   .group_by(self._dim_inst_hier.c.school_name, self._dim_inst_hier.c.school_guid)\
                   .order_by(self._dim_inst_hier.c.school_name)

    def get_query_for_school_view(self):
        return self.build_query(select_with_context, [self._fact_asmt_outcome.c.asmt_grade.label(Constants.NAME), self._fact_asmt_outcome.c.asmt_grade.label(Constants.ID)])\
                   .group_by(self._fact_asmt_outcome.c.asmt_grade)\
                   .where(and_(self._fact_asmt_outcome.c.district_guid == self._district_guid, self._fact_asmt_outcome.c.school_guid == self._school_guid))\
                   .order_by(self._fact_asmt_outcome.c.asmt_subject.desc(), self._fact_asmt_outcome.c.asmt_grade)
