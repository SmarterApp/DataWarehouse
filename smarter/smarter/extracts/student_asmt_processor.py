from datetime import datetime
import os
import copy
import re
from pyramid.threadlocal import get_current_registry
from sqlalchemy.sql.expression import and_
from smarter.extracts import processor
from smarter.reports.helpers.constants import Constants
from smarter.reports.helpers.constants import AssessmentType
from smarter.extracts.constants import Constants as Extract, ExtractType
from edcore.database.edcore_connector import EdCoreDBConnection
from smarter.extracts.student_assessment import get_extract_assessment_query, get_extract_assessment_query_iab, get_extract_assessment_item_and_raw_query, \
    get_required_permission, get_extract_assessment_item_and_raw_count_query
from edcore.utils.utils import compile_query_to_sql_text, merge_dict
from edcore.security.tenant import get_state_code_to_tenant_map
from edextract.status.status import create_new_entry
from edapi.exceptions import NotFoundException
from smarter.security.context import select_with_context
from smarter.extracts.metadata import get_metadata_file_name, get_asmt_metadata
from edextract.tasks.constants import Constants as TaskConstants, ExtractionDataType, QueryType
from hpz_client.frs.file_registration import register_file
from smarter.reports.helpers.filters import has_filters, FILTERS_CONFIG, \
    apply_filter_to_query
from smarter.extracts.utils import start_extract, generate_extract_file_tasks
from edextract.tasks.extract import archive_with_stream, prepare_path


__author__ = 'ablum'


def process_extraction_request(params, is_async=True):
    '''
    :param dict params: contains query parameter.  Value for each pair is expected to be a list
    :param bool is_tenant_level:  True if it is a tenant level request
    '''
    tasks = []
    response = {}
    task_responses = []
    filter_params = {}
    state_code = params[Constants.STATECODE][0]
    districts = params.get(Constants.DISTRICTGUID, [None])
    schools = params.get(Constants.SCHOOLGUID, [None])
    grades = params.get(Constants.ASMTGRADE, [None])
    request_id, user, tenant = processor.get_extract_request_user_info(state_code)

    # This is purely for file name conventions (for async extracts), consider refactoring
    is_tenant_level = is_async

    # Get filter related parameters
    if has_filters(params):
        filter_params = {k: v for k, v in params.items() if k in FILTERS_CONFIG}

    for district in districts:
        for school in schools:
            for grade in grades:
                for s in params[Constants.ASMTSUBJECT]:
                    for t in params[Constants.ASMTTYPE]:
                        param = merge_dict({Constants.ASMTSUBJECT: s,
                                            Constants.ASMTTYPE: t,
                                            Constants.ASMTYEAR: params[Constants.ASMTYEAR][0],
                                            Constants.STATECODE: state_code,
                                            Constants.SCHOOLGUID: school,
                                            Constants.DISTRICTGUID: district,
                                            Constants.ASMTGRADE: grade,
                                            Constants.STUDENTGUID: params.get(Constants.STUDENTGUID)}, filter_params)

                        task_response = {Constants.STATECODE: param[Constants.STATECODE],
                                         Constants.DISTRICTGUID: district,
                                         Constants.SCHOOLGUID: school,
                                         Extract.EXTRACTTYPE: ExtractType.studentAssessment,
                                         Constants.ASMTSUBJECT: param[Constants.ASMTSUBJECT],
                                         Constants.ASMTTYPE: param[Constants.ASMTTYPE],
                                         Constants.ASMTYEAR: param[Constants.ASMTYEAR],
                                         Extract.REQUESTID: request_id}

                        # separate by grades if no grade is specified
                        __tasks, __task_responses = _create_tasks_with_responses(request_id, user, tenant, param, task_response, is_tenant_level=is_tenant_level)
                        tasks += __tasks
                        task_responses += __task_responses
    if is_async:
        response['tasks'] = task_responses
        if tasks:
            response[Constants.FILES] = []
            files = {}
            archive_file_name = processor.get_archive_file_path(user.get_uid(), tenant, request_id)
            files[Constants.FILENAME] = os.path.basename(archive_file_name)
            directory_to_archive = processor.get_extract_work_zone_path(tenant, request_id)

            # Register extract file with HPZ.
            registration_id, download_url, web_download_url = register_file(user.get_uid())
            files[Constants.DOWNLOAD_URL] = download_url
            files[Constants.WEB_DOWNLOAD_URL] = web_download_url

            response[Constants.FILES].append(files)

            queue = get_current_registry().settings.get('extract.job.queue.async', TaskConstants.DEFAULT_QUEUE_NAME)
            start_extract(tenant, request_id, [archive_file_name], [directory_to_archive], [registration_id], tasks, queue=queue)
        return response
    else:
        if tasks:
            settings = get_current_registry().settings
            queue = settings.get('extract.job.queue.sync', TaskConstants.SYNC_QUEUE_NAME)
            archive_queue = settings.get('extract.job.queue.archive', TaskConstants.ARCHIVE_QUEUE_NAME)
            directory_to_archive = processor.get_extract_work_zone_path(tenant, request_id)
            celery_timeout = int(get_current_registry().settings.get('extract.celery_timeout', '30'))
            # Synchronous calls to generate json and csv and then to archive
            # BUG, it still routes to 'extract' queue due to chain
    #        result = chain(prepare_path.subtask(args=[tenant, request_id, [directory_to_archive]], queue=queue, immutable=True),      # @UndefinedVariable
    #                       route_tasks(tenant, request_id, tasks, queue_name=queue),
    #                       archive.subtask(args=[request_id, directory_to_archive], queue=archive_queue, immutable=True)).delay()
            prepare_path.apply_async(args=[request_id, [directory_to_archive]], queue=queue, immutable=True).get(timeout=celery_timeout)  # @UndefinedVariable
            generate_extract_file_tasks(tenant, request_id, tasks, queue_name=queue)().get(timeout=celery_timeout)
            result = archive_with_stream.apply_async(args=[request_id, directory_to_archive], queue=archive_queue, immutable=True)
            return result.get(timeout=celery_timeout)
        else:
            raise NotFoundException("There are no results")


def estimate_extract_total_file_size(params, avg_file_size, extract_type):
    """
    returns an estimate of the number of extract files based on query params and extract type

    @param params: Extract query params
    """
    return_number = -1
    state_code = params.get(Constants.STATECODE)
    with EdCoreDBConnection(state_code=state_code) as connector:
        query = get_extract_assessment_item_and_raw_count_query(params, extract_type)
        results = connector.get_result(query)
        return_number = results[0][Constants.COUNT]
    if return_number > 0:
        if avg_file_size > 0:
            return return_number * avg_file_size
    return 0


def process_async_item_or_raw_extraction_request(params, extract_type):
    '''
    :param dict params: contains query parameter.  Value for each pair is expected to be a list
    :param bool is_tenant_level:  True if it is a tenant level request
    '''
    queue = get_current_registry().settings.get('extract.job.queue.async', TaskConstants.DEFAULT_QUEUE_NAME)
    soft_limit = int(get_current_registry().settings.get('extract.partial_file.size.soft_limit', '-1'))
    if extract_type is ExtractType.itemLevel:
        average_size = int(get_current_registry().settings.get('extract.partial_file.size.average.csv', '-1'))
    else:
        average_size = int(get_current_registry().settings.get('extract.partial_file.size.average.xml', '-1'))
    data_path_config_key = 'extract.item_level_base_dir' if extract_type is ExtractType.itemLevel else 'extract.raw_data_base_dir'
    root_dir = get_current_registry().settings.get(data_path_config_key)
    response = {}
    state_code = params[Constants.STATECODE]
    request_id, user, tenant = processor.get_extract_request_user_info(state_code)
    extract_params = copy.deepcopy(params)
    base_directory_to_archive = processor.get_extract_work_zone_path(tenant, request_id)

    # get an estimate for number of extract files that needs to be created based on the params
    # parts = estimate_extract_files(params=params, extract_type=extract_type)

    # temp hack till estimator is fixed. Needs to be removed and substituted with above line
    estimated_total_files = 1
    estimated_total_size = estimate_extract_total_file_size(params, average_size, extract_type)

    # No data available
    if estimated_total_size is 0:
        task_response = {}
        task_response[Extract.STATUS] = Extract.NO_DATA
        task_response[Extract.MESSAGE] = "Data is not available"
        response['tasks'] = [task_response]
    else:
        if soft_limit > 0:
            estimated_total_files = int(estimated_total_size / soft_limit)
            if estimated_total_size % soft_limit > 0:
                estimated_total_files += 1

        out_file_names = []
        directories_to_archive = []
        extract_files = []
        archive_files = []
        registration_ids = []

        for estimated_total_file in range(estimated_total_files):
            extract_file = {}
            if extract_type is ExtractType.itemLevel:
                out_file_names.append(get_items_extract_file_path(extract_params, tenant, request_id, partial_no=estimated_total_file if estimated_total_files > 1 else None))
            if estimated_total_files > 1:
                directories_to_archive.append(os.path.join(base_directory_to_archive, 'part' + str(estimated_total_file)))
                archive_file_name = processor.get_archive_file_path(user.get_uid(), tenant, request_id, partial_no=estimated_total_file)
            else:
                directories_to_archive.append(base_directory_to_archive)
                archive_file_name = processor.get_archive_file_path(user.get_uid(), tenant, request_id)
            archive_files.append(archive_file_name)
            registration_id, download_url, web_download_url = register_file(user.get_uid())
            registration_ids.append(registration_id)
            extract_file[Constants.FILENAME] = os.path.basename(archive_file_name)
            extract_file[Constants.DOWNLOAD_URL] = download_url
            extract_file[Constants.WEB_DOWNLOAD_URL] = web_download_url
            extract_files.append(extract_file)

        tasks, task_responses = _create_item_or_raw_tasks_with_responses(request_id, user, extract_params, root_dir, out_file_names, directories_to_archive, extract_type)
        response['tasks'] = task_responses
        response['files'] = extract_files
        start_extract(tenant, request_id, archive_files, directories_to_archive, registration_ids, tasks, queue=queue)
    return response


def _get_asmt_records(param, extract_type):
    '''
    query all asmt_guid and asmt_grade by given extract request params
    '''
    asmt_type = param.get(Constants.ASMTTYPE)
    asmt_subject = param.get(Constants.ASMTSUBJECT)
    state_code = param.get(Constants.STATECODE)
    district_id = param.get(Constants.DISTRICTGUID)
    school_id = param.get(Constants.SCHOOLGUID)
    asmt_grade = param.get(Constants.ASMTGRADE)
    asmt_year = param.get(Constants.ASMTYEAR)
    student_id = param.get(Constants.STUDENTGUID)
    # TODO: remove dim_asmt
    with EdCoreDBConnection(state_code=state_code) as connector:
        dim_asmt = connector.get_table(Constants.DIM_ASMT)
        fact_asmt_outcome_vw = connector.get_table(Constants.FACT_ASMT_OUTCOME_VW)
        dim_student = connector.get_table(Constants.DIM_STUDENT)
        query = select_with_context([dim_asmt.c.asmt_guid.label(Constants.ASMT_GUID),
                                     fact_asmt_outcome_vw.c.asmt_grade.label(Constants.ASMT_GRADE)],
                                    from_obj=[dim_asmt
                                              .join(fact_asmt_outcome_vw, and_(dim_asmt.c.asmt_rec_id == fact_asmt_outcome_vw.c.asmt_rec_id))], permission=get_required_permission(extract_type), state_code=state_code)\
            .where(and_(fact_asmt_outcome_vw.c.state_code == state_code))\
            .where(and_(fact_asmt_outcome_vw.c.asmt_type == asmt_type))\
            .where(and_(fact_asmt_outcome_vw.c.asmt_subject == asmt_subject))\
            .where(and_(fact_asmt_outcome_vw.c.rec_status == Constants.CURRENT))\
            .group_by(dim_asmt.c.asmt_guid, fact_asmt_outcome_vw.c.asmt_grade)

        if district_id is not None:
            query = query.where(and_(fact_asmt_outcome_vw.c.district_id == district_id))
        if school_id is not None:
            query = query.where(and_(fact_asmt_outcome_vw.c.school_id == school_id))
        if asmt_grade is not None:
            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_grade == asmt_grade))
        if asmt_year is not None:
            query = query.where(and_(fact_asmt_outcome_vw.c.asmt_year == asmt_year))
        if student_id:
            query = query.where(and_(fact_asmt_outcome_vw.c.student_id.in_(student_id)))

        query = apply_filter_to_query(query, fact_asmt_outcome_vw, dim_student, param)
        results = connector.get_result(query)
    return results


def _get_asmt_records_iab(param, extract_type):
    '''
    query all asmt_guid and asmt_grade by given extract request params
    '''
    asmt_type = param.get(Constants.ASMTTYPE)
    asmt_subject = param.get(Constants.ASMTSUBJECT)
    state_code = param.get(Constants.STATECODE)
    district_id = param.get(Constants.DISTRICTGUID)
    school_id = param.get(Constants.SCHOOLGUID)
    asmt_grade = param.get(Constants.ASMTGRADE)
    asmt_year = param.get(Constants.ASMTYEAR)
    student_id = param.get(Constants.STUDENTGUID)
    # TODO: remove dim_asmt
    with EdCoreDBConnection(state_code=state_code) as connector:
        dim_asmt = connector.get_table(Constants.DIM_ASMT)
        fact_block_asmt_outcome = connector.get_table(Constants.FACT_BLOCK_ASMT_OUTCOME)
        dim_student = connector.get_table(Constants.DIM_STUDENT)
        query = select_with_context([dim_asmt.c.asmt_guid.label(Constants.ASMT_GUID),
                                     dim_asmt.c.effective_date.label(Constants.EFFECTIVE_DATE),
                                     dim_asmt.c.asmt_claim_1_name.label(Constants.ASMT_CLAIM_1_NAME),
                                     fact_block_asmt_outcome.c.asmt_grade.label(Constants.ASMT_GRADE)],
                                    from_obj=[dim_asmt
                                              .join(fact_block_asmt_outcome, and_(dim_asmt.c.asmt_rec_id == fact_block_asmt_outcome.c.asmt_rec_id))], permission=get_required_permission(extract_type), state_code=state_code)\
            .where(and_(fact_block_asmt_outcome.c.state_code == state_code))\
            .where(and_(fact_block_asmt_outcome.c.asmt_type == asmt_type))\
            .where(and_(fact_block_asmt_outcome.c.asmt_subject == asmt_subject))\
            .where(and_(fact_block_asmt_outcome.c.rec_status == Constants.CURRENT))\
            .group_by(dim_asmt.c.asmt_guid, dim_asmt.c.effective_date, dim_asmt.c.asmt_claim_1_name, fact_block_asmt_outcome.c.asmt_grade)

        if district_id is not None:
            query = query.where(and_(fact_block_asmt_outcome.c.district_id == district_id))
        if school_id is not None:
            query = query.where(and_(fact_block_asmt_outcome.c.school_id == school_id))
        if asmt_grade is not None:
            query = query.where(and_(fact_block_asmt_outcome.c.asmt_grade == asmt_grade))
        if asmt_year is not None:
            query = query.where(and_(fact_block_asmt_outcome.c.asmt_year == asmt_year))
        if student_id:
            query = query.where(and_(fact_block_asmt_outcome.c.student_id.in_(student_id)))

        query = apply_filter_to_query(query, fact_block_asmt_outcome, dim_student, param)
        results = connector.get_result(query)
    return results


PREQUERY_FUNCTIONS = {
    AssessmentType.INTERIM_ASSESSMENT_BLOCKS: _get_asmt_records_iab,
    AssessmentType.SUMMATIVE: _get_asmt_records,
    AssessmentType.INTERIM_COMPREHENSIVE: _get_asmt_records
}


def _prepare_data(param, extract_type):
    '''
    Prepare record for available pre-query extract
    '''
    asmt_guid_with_grades = []
    dim_asmt = None
    fact_table = None
    FACT_TABLE = {
        AssessmentType.INTERIM_ASSESSMENT_BLOCKS: Constants.FACT_BLOCK_ASMT_OUTCOME,
        AssessmentType.SUMMATIVE: Constants.FACT_ASMT_OUTCOME_VW,
        AssessmentType.INTERIM_COMPREHENSIVE: Constants.FACT_ASMT_OUTCOME_VW
    }

    prequery_func = PREQUERY_FUNCTIONS[param['asmtType']]
    available_records = prequery_func(param, extract_type)
    for record_by_asmt_type in available_records:
        record = (record_by_asmt_type[Constants.ASMT_GUID], record_by_asmt_type[Constants.ASMT_GRADE])
        if (Constants.EFFECTIVE_DATE in record_by_asmt_type):
            # IAB records
            record_iab = (record_by_asmt_type[Constants.EFFECTIVE_DATE], record_by_asmt_type[Constants.ASMT_CLAIM_1_NAME])
        else:
            record_iab = ()
        asmt_guid_with_grades.append(record + record_iab)

    if asmt_guid_with_grades:
        with EdCoreDBConnection(state_code=param.get(Constants.STATECODE)) as connector:
            dim_asmt = connector.get_table(Constants.DIM_ASMT)
            fact_table = connector.get_table(FACT_TABLE[param['asmtType']])
    # Returns list of asmt guid with grades, and table objects
    return asmt_guid_with_grades, dim_asmt, fact_table


EXTRACT_FUNCTIONS = {
    AssessmentType.INTERIM_ASSESSMENT_BLOCKS: get_extract_assessment_query_iab,
    AssessmentType.SUMMATIVE: get_extract_assessment_query,
    AssessmentType.INTERIM_COMPREHENSIVE: get_extract_assessment_query
}


def _create_tasks_with_responses(request_id, user, tenant, param, task_response={}, is_tenant_level=False):
    '''
    TODO comment
    '''
    tasks = []
    task_responses = []
    copied_task_response = copy.deepcopy(task_response)
    effective_date = ''
    asmt_claim_1_name = ''
    guid_grade, dim_asmt, fact_table = _prepare_data(param, ExtractType.studentAssessment)

    copied_params = copy.deepcopy(param)
    copied_params[Constants.ASMTGRADE] = None
    query_func = EXTRACT_FUNCTIONS[param['asmtType']]
    query = query_func(copied_params)
    if guid_grade:
        for asmt_record in guid_grade:
            if len(asmt_record) == 2:
                asmt_guid, asmt_grade = asmt_record
            else:
                asmt_guid, asmt_grade, effective_date, asmt_claim_1_name = asmt_record
            copied_params = copy.deepcopy(param)
            copied_params[Constants.ASMTGUID] = asmt_guid
            copied_params[Constants.ASMTGRADE] = asmt_grade
            copied_params[Constants.EFFECTIVE_DATE] = effective_date
            copied_params[Constants.ASMT_CLAIM_1_NAME] = asmt_claim_1_name
            query_with_asmt_rec_id_and_asmt_grade = query.where(and_(dim_asmt.c.asmt_guid == asmt_guid))
            query_with_asmt_rec_id_and_asmt_grade = query_with_asmt_rec_id_and_asmt_grade.where(and_(fact_table.c.asmt_grade == asmt_grade))
            tasks += (_create_tasks(request_id, user, tenant, copied_params, query_with_asmt_rec_id_and_asmt_grade,
                                    is_tenant_level=is_tenant_level))
        copied_task_response[Extract.STATUS] = Extract.OK
        task_responses.append(copied_task_response)
    else:
        copied_task_response[Extract.STATUS] = Extract.NO_DATA
        copied_task_response[Extract.MESSAGE] = "Data is not available"
        task_responses.append(copied_task_response)
    return tasks, task_responses


def _create_item_or_raw_tasks_with_responses(request_id, user, param, root_dir, out_files, directories_to_archive,
                                             extract_type, task_response={}, is_tenant_level=False):
    '''
    TODO comment
    '''
    tasks = []
    task_responses = []
    copied_task_response = copy.deepcopy(task_response)
    states_to_tenants = get_state_code_to_tenant_map()
    guid_grade, _, _ = _prepare_data(param, extract_type)

    if guid_grade:
        state_code = param.get(Constants.STATECODE)
        query = get_extract_assessment_item_and_raw_query(param, extract_type)
        tenant = states_to_tenants[state_code]
        task = _create_new_task(request_id, user, tenant, param, query,
                                is_tenant_level=is_tenant_level, extract_type=extract_type)
        task[TaskConstants.TASK_FILE_NAME] = out_files
        task[TaskConstants.ROOT_DIRECTORY] = root_dir
        task[TaskConstants.DIRECTORY_TO_ARCHIVE] = directories_to_archive
        if extract_type is ExtractType.itemLevel:
            task[TaskConstants.ITEM_IDS] = param.get(Constants.ITEMID) if Constants.ITEMID in param else None
        tasks.append(task)
        copied_task_response[Extract.STATUS] = Extract.OK
        task_responses.append(copied_task_response)
    else:
        copied_task_response[Extract.STATUS] = Extract.NO_DATA
        copied_task_response[Extract.MESSAGE] = "Data is not available"
        task_responses.append(copied_task_response)
    return tasks, task_responses


def _create_tasks(request_id, user, tenant, params, query, is_tenant_level=False):
    '''
    TODO comment
    '''
    tasks = []
    tasks.append(_create_new_task(request_id, user, tenant, params, query, is_tenant_level=is_tenant_level,
                                  extract_file_path=get_extract_file_path))
    tasks.append(_create_asmt_metadata_task(request_id, user, tenant, params))
    return tasks


def _create_asmt_metadata_task(request_id, user, tenant, params):
    '''
    TODO comment
    '''
    query = get_asmt_metadata(params.get(Constants.STATECODE), params.get(Constants.ASMTGUID))
    return _create_new_task(request_id, user, tenant, params, query, asmt_metadata=True)


def _create_new_task(request_id, user, tenant, params, query, extract_type=None, asmt_metadata=False, is_tenant_level=False,
                     extract_file_path=None):
    '''
    TODO comment
    '''
    task = {}
    task[TaskConstants.TASK_TASK_ID] = create_new_entry(user, request_id, params)
    task[TaskConstants.TASK_QUERIES] = {QueryType.QUERY: compile_query_to_sql_text(query)}
    if asmt_metadata:
        task[TaskConstants.TASK_FILE_NAME] = get_asmt_metadata_file_path(params, tenant, request_id)
        task[TaskConstants.EXTRACTION_DATA_TYPE] = ExtractionDataType.QUERY_JSON
    else:
        if extract_file_path is not None:
            task[TaskConstants.TASK_FILE_NAME] = extract_file_path(params, tenant, request_id,
                                                                   is_tenant_level=is_tenant_level)
        if extract_type and extract_type is ExtractType.itemLevel:
            task[TaskConstants.EXTRACTION_DATA_TYPE] = ExtractionDataType.QUERY_ITEMS_CSV
        elif extract_type and extract_type is ExtractType.rawData:
            task[TaskConstants.EXTRACTION_DATA_TYPE] = ExtractionDataType.QUERY_RAW_XML
        else:
            task[TaskConstants.EXTRACTION_DATA_TYPE] = ExtractionDataType.QUERY_CSV
    return task


def get_extract_file_path(param, tenant, request_id, is_tenant_level=False):
    FILENAME_FUNC = {AssessmentType.INTERIM_ASSESSMENT_BLOCKS: get_file_name_iab}
    identifier = '_' + param.get(Constants.STATECODE) if is_tenant_level else ''
    filename_func = FILENAME_FUNC.get(param['asmtType'], get_file_name)
    file_name = filename_func(param, identifier)
    return os.path.join(processor.get_extract_work_zone_path(tenant, request_id), file_name)


def get_file_name(param, identifier):
    file_name = 'ASMT_{asmtYear}{identifier}_{asmtGrade}_{asmtSubject}_{asmtType}_{currentTime}_{asmtGuid}.csv'.\
                format(identifier=identifier,
                       asmtGrade=('GRADE_' + param.get(Constants.ASMTGRADE)).upper(),
                       asmtSubject=param[Constants.ASMTSUBJECT].upper(),
                       asmtType=param[Constants.ASMTTYPE].upper(),
                       currentTime=str(datetime.now().strftime("%m-%d-%Y_%H-%M-%S")),
                       asmtYear=param[Constants.ASMTYEAR],
                       asmtGuid=param[Constants.ASMTGUID])
    return file_name


def get_file_name_iab(param, identifier):
    asmt_claim_1_name = param[Constants.ASMT_CLAIM_1_NAME]
    asmt_claim_1_name = re.sub(r'[^a-zA-Z0-9]', '_', asmt_claim_1_name)
    file_name = 'ASMT_{asmtYear}{identifier}_{asmtGrade}_{asmtSubject}_IAB_{asmt_claim_1_name}_EFF{effectiveDate}_TS{currentTime}_{asmtGuid}.csv'.\
                format(identifier=identifier,
                       asmtGrade=('GRADE_' + param.get(Constants.ASMTGRADE)).upper(),
                       asmtSubject=param[Constants.ASMTSUBJECT].upper(),
                       asmtType=param[Constants.ASMTTYPE].upper(),
                       currentTime=str(datetime.now().strftime("%m-%d-%Y_%H-%M-%S")),
                       asmtYear=param[Constants.ASMTYEAR],
                       asmtGuid=param[Constants.ASMTGUID],
                       effectiveDate=datetime.strptime(param[Constants.EFFECTIVE_DATE], '%Y%m%d').strftime('%m-%d-%Y'),
                       asmt_claim_1_name=asmt_claim_1_name)
    return file_name


def get_items_extract_file_path(param, tenant, request_id, partial_no=None):
    file_name = '{prefix}_{stateCode}_{asmtYear}_{asmtType}_{asmtSubject}_GRADE_{asmtGrade}_{currentTime}{partial_no}.csv'.\
                format(prefix='ITEMS',
                       stateCode=param[Constants.STATECODE],
                       asmtYear=param[Constants.ASMTYEAR],
                       asmtType=param[Constants.ASMTTYPE].upper(),
                       asmtSubject=param[Constants.ASMTSUBJECT].upper(),
                       asmtGrade=param.get(Constants.ASMTGRADE),
                       currentTime=str(datetime.now().strftime("%m-%d-%Y_%H-%M-%S")),
                       partial_no='_part' + str(partial_no) if partial_no is not None else '')
    return os.path.join(processor.get_extract_work_zone_path(tenant, request_id),
                        'part' + str(partial_no) if partial_no is not None else '', file_name)


def get_asmt_metadata_file_path(params, tenant, request_id):
    return os.path.join(processor.get_extract_work_zone_path(tenant, request_id), get_metadata_file_name(params))
