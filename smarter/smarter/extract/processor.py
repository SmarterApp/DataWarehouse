'''
Celery Tasks for data extraction

Created on Nov 5, 2013

@author: ejen
'''
import logging
from smarter.reports.helpers.constants import Constants
from smarter.extract.constants import Constants as Extract, ExtractType
from edcore.database.edcore_connector import EdCoreDBConnection
from smarter.extract.student_assessment import get_extract_assessment_query, compile_query_to_sql_text
from pyramid.security import authenticated_userid
from uuid import uuid4
from edextract.status.status import create_new_entry
from edextract.tasks.extract import start_extract, archive, route_tasks
from pyramid.threadlocal import get_current_request, get_current_registry
from datetime import datetime
import os
import tempfile
from edapi.exceptions import NotFoundException
import copy
from smarter.security.context import select_with_context
from sqlalchemy.sql.expression import and_
from smarter.extract.metadata import get_metadata_file_name, get_asmt_metadata
from edextract.tasks.constants import Constants as TaskConstants
from edapi.cache import cache_region


log = logging.getLogger('smarter')


def process_sync_extract_request(params):
    tasks = []
    request_id, user, tenant = _get_extract_request_user_info()
    extract_params = copy.deepcopy(params)
    for subject in params[Constants.ASMTSUBJECT]:
        extract_params[Constants.ASMTSUBJECT] = subject
        subject_tasks, task_responses = _create_tasks_with_responses(request_id, user, tenant, extract_params)
        tasks += subject_tasks
    if tasks:
        directory_to_archive = get_extract_work_zone_path(tenant, request_id)
        celery_timeout = int(get_current_registry().settings.get('extract.celery_timeout', '30'))
        # Synchronous calls to generate json and csv and then to archive
        route_tasks(tenant, request_id, tasks, queue_name=TaskConstants.SYNC_QUEUE_NAME)().get(timeout=celery_timeout)
        result = archive.apply_async(args=[request_id, directory_to_archive], queue=TaskConstants.SYNC_QUEUE_NAME)
        return result.get(timeout=celery_timeout)
    else:
        raise NotFoundException("There are no results")


def process_async_extraction_request(params, is_tenant_level=True):
    '''
    :param dict params: contains query parameter.  Value for each pair is expected to be a list
    :param bool is_tenant_level:  True if it is a tenant level request
    '''
    tasks = []
    response = {}
    task_responses = []
    request_id, user, tenant = _get_extract_request_user_info()

    for s in params[Constants.ASMTSUBJECT]:
        for t in params[Constants.ASMTTYPE]:
            # TODO: handle year and stateCode/tenant
            param = ({Constants.ASMTSUBJECT: s,
                     Constants.ASMTTYPE: t,
                     Constants.ASMTYEAR: params[Constants.ASMTYEAR][0],
                     Constants.STATECODE: params[Constants.STATECODE][0]})

            task_response = {Constants.STATECODE: param[Constants.STATECODE],
                             Extract.EXTRACTTYPE: ExtractType.studentAssessment,
                             Constants.ASMTSUBJECT: param[Constants.ASMTSUBJECT],
                             Constants.ASMTTYPE: param[Constants.ASMTTYPE],
                             # Constants.ASMTYEAR: task[Constants.ASMTYEAR],
                             Extract.REQUESTID: request_id}

            # separate by grades if no grade is specified
            __tasks, __task_responses = _create_tasks_with_responses(request_id, user, tenant, param, task_response, is_tenant_level=is_tenant_level)
            tasks += __tasks
            task_responses += __task_responses

    response['tasks'] = task_responses
    if len(tasks) > 0:
        # TODO: handle empty public key
        public_key_id = get_encryption_public_key_identifier(tenant)
        archive_file_name = get_archive_file_path(user.get_uid(), tenant, request_id)
        response['fileName'] = os.path.basename(archive_file_name)
        directory_to_archive = get_extract_work_zone_path(tenant, request_id)
        gatekeeper_id = get_gatekeeper(tenant)
        pickup_zone_info = get_pickup_zone_info(tenant)
        start_extract.apply_async(args=[tenant, request_id, public_key_id, archive_file_name, directory_to_archive, gatekeeper_id, pickup_zone_info, tasks], queue='extract')  # @UndefinedVariable
    return response


@cache_region('public.shortlived')
def _get_asmt_records(state_code):
    '''
    query all available record for asmt_guid and asmt_grade by given state_code.
    return format {'ELA': {'SUMMATIVE': ['…'], 'COMP': ['…']}, 'MATH': {'SUMMATIVE': ['…'] ...
    '''
    keys = {}
    with EdCoreDBConnection() as connector:
        dim_asmt = connector.get_table(Constants.DIM_ASMT)
        fact_asmt_outcome = connector.get_table(Constants.FACT_ASMT_OUTCOME)
        query = select_with_context([dim_asmt.c.asmt_guid.label(Constants.ASMT_GUID),
                                     fact_asmt_outcome.c.asmt_grade.label(Constants.ASMT_GRADE),
                                     dim_asmt.c.asmt_type.label(Constants.ASMTTYPE),
                                     dim_asmt.c.asmt_subject.label(Constants.ASMTSUBJECT),
                                     fact_asmt_outcome.c.school_guid.label(Constants.SCHOOL_GUID),
                                     fact_asmt_outcome.c.district_guid.label(Constants.DISTRICT_GUID),
                                     fact_asmt_outcome.c.asmt_year.label(Constants.ASMT_YEAR)],
                                    from_obj=[dim_asmt
                                              .join(fact_asmt_outcome, and_(dim_asmt.c.asmt_rec_id == fact_asmt_outcome.c.asmt_rec_id))])\
            .where(and_(fact_asmt_outcome.c.state_code == state_code))\
            .group_by(dim_asmt.c.asmt_guid, fact_asmt_outcome.c.asmt_grade, dim_asmt.c.asmt_type, dim_asmt.c.asmt_subject,
                      fact_asmt_outcome.c.school_guid, fact_asmt_outcome.c.district_guid, fact_asmt_outcome.c.asmt_year)

        results = connector.get_result(query)
        for result in results:
            asmt_guid = result[Constants.ASMT_GUID]
            asmt_grade = result[Constants.ASMT_GRADE]
            asmt_type = result[Constants.ASMTTYPE]
            asmt_subject = result[Constants.ASMTSUBJECT]
            school_guid = result[Constants.SCHOOL_GUID]
            district_guid = result[Constants.DISTRICT_GUID]
            asmt_year = result[Constants.ASMT_YEAR]

            asmt_subjects = keys.get(asmt_subject, {})
            if not asmt_subjects:
                keys[asmt_subject] = asmt_subjects
            asmt_types = asmt_subjects.get(asmt_type, [])
            if not asmt_types:
                asmt_subjects[asmt_type] = asmt_types
            asmt_types.append({Constants.ASMT_GUID: asmt_guid, Constants.ASMT_GRADE: asmt_grade,
                               Constants.SCHOOL_GUID: school_guid, Constants.DISTRICT_GUID: district_guid,
                               Constants.ASMT_YEAR: str(asmt_year) if asmt_year is not None else ''})
    return keys


def _prepare_data(param):
    '''
    Prepare record for available pre-query extract
    '''
    guid_grade_map = {}
    dim_asmt = None
    fact_asmt_outcome = None
    asmt_grade = param.get(Constants.ASMTGRADE)
    asmt_type = param.get(Constants.ASMTTYPE)
    asmt_subject = param.get(Constants.ASMTSUBJECT)
    state_code = param.get(Constants.STATECODE)
    district_guid = param.get(Constants.DISTRICTGUID)
    school_guid = param.get(Constants.SCHOOLGUID)
    asmt_year = param.get(Constants.ASMTYEAR)
    available_records = _get_asmt_records(state_code)
    records_by_asmt_subject = available_records.get(asmt_subject, {})
    records_by_asmt_type = records_by_asmt_subject.get(asmt_type, [])
    for record_by_asmt_type in records_by_asmt_type:
        if asmt_grade is not None and record_by_asmt_type[Constants.ASMT_GRADE] != asmt_grade:
            pass
        elif district_guid is not None and record_by_asmt_type[Constants.DISTRICT_GUID] != district_guid:
            pass
        elif school_guid is not None and record_by_asmt_type[Constants.SCHOOL_GUID] != school_guid:
            pass
        elif asmt_year is not None and record_by_asmt_type[Constants.ASMT_YEAR] != asmt_year:
            pass
        else:
            guid_grade_map_key = record_by_asmt_type[Constants.ASMT_GUID] + ':' + record_by_asmt_type[Constants.ASMT_GRADE]
            if guid_grade_map_key not in guid_grade_map:
                guid_grade_map[guid_grade_map_key] = (record_by_asmt_type[Constants.ASMT_GUID], record_by_asmt_type[Constants.ASMT_GRADE])

    if guid_grade_map:
        with EdCoreDBConnection() as connector:
            dim_asmt = connector.get_table(Constants.DIM_ASMT)
            fact_asmt_outcome = connector.get_table(Constants.FACT_ASMT_OUTCOME)
    return list(guid_grade_map.values()), dim_asmt, fact_asmt_outcome


def _create_tasks_with_responses(request_id, user, tenant, param, task_response={}, is_tenant_level=False):
    '''
    TODO comment
    '''
    tasks = []
    task_responses = []
    copied_task_response = copy.deepcopy(task_response)
    guid_grade, dim_asmt, fact_asmt_outcome = _prepare_data(param)

    copied_params = copy.deepcopy(param)
    copied_params[Constants.ASMTGRADE] = None
    query = get_extract_assessment_query(copied_params)
    if guid_grade:
        for asmt_guid, asmt_grade in guid_grade:
            copied_params[Constants.ASMTGUID] = asmt_guid
            copied_params[Constants.ASMTGRADE] = asmt_grade
            query_with_asmt_rec_id_and_asmt_grade = query.where(and_(dim_asmt.c.asmt_guid == asmt_guid))\
                .where(and_(fact_asmt_outcome.c.asmt_grade == asmt_grade))
            tasks += (_create_tasks(request_id, user, tenant, copied_params, query_with_asmt_rec_id_and_asmt_grade, is_tenant_level=is_tenant_level))
        copied_task_response[Extract.STATUS] = Extract.OK
        task_responses.append(copied_task_response)
    else:
        copied_task_response[Extract.STATUS] = Extract.FAIL
        copied_task_response[Extract.MESSAGE] = "Data is not available"
        task_responses.append(copied_task_response)
    return tasks, task_responses


def _create_tasks(request_id, user, tenant, params, query, is_tenant_level=False):
    '''
    TODO comment
    '''
    tasks = []
    tasks.append(_create_new_task(request_id, user, tenant, params, query, is_tenant_level=is_tenant_level))
    tasks.append(_create_asmt_metadata_task(request_id, user, tenant, params))
    return tasks


def _create_asmt_metadata_task(request_id, user, tenant, params):
    '''
    TODO comment
    '''
    query = get_asmt_metadata(params.get(Constants.ASMTGUID))
    return _create_new_task(request_id, user, tenant, params, query, asmt_metadata=True)


def _create_new_task(request_id, user, tenant, params, query, asmt_metadata=False, is_tenant_level=False):
    '''
    TODO comment
    '''
    task = {}
    task[TaskConstants.TASK_TASK_ID] = create_new_entry(user, request_id, params)
    if asmt_metadata:
        task[TaskConstants.TASK_FILE_NAME] = get_asmt_metadata_file_path(params, tenant, request_id)
        task[TaskConstants.TASK_IS_JSON_REQUEST] = True
    else:
        task[TaskConstants.TASK_FILE_NAME] = get_extract_file_path(params, tenant, request_id, is_tenant_level=is_tenant_level)
        task[TaskConstants.TASK_IS_JSON_REQUEST] = False
    task[TaskConstants.TASK_QUERY] = compile_query_to_sql_text(query)
    return task


def _get_extract_request_user_info():
    # Generate an uuid for this extract request
    request_id = str(uuid4())
    user = authenticated_userid(get_current_request())
    tenant = user.get_tenant()
    return request_id, user, tenant


def _get_extract_work_zone_base_dir():
    return get_current_registry().settings.get('extract.work_zone_base_dir', tempfile.gettempdir())


def get_extract_work_zone_path(tenant, request_id):
    base = _get_extract_work_zone_base_dir()
    return os.path.join(base, tenant, request_id, 'data')


def get_extract_file_path(param, tenant, request_id, is_tenant_level=False):
    identifier = '_' + param.get(Constants.STATECODE) if is_tenant_level else ''
    file_name = 'ASMT{identifier}_{asmtGrade}_{asmtSubject}_{asmtType}_{currentTime}_{asmtGuid}.csv'.format(identifier=identifier,
                                                                                                            asmtGrade=('GRADE_' + param.get(Constants.ASMTGRADE)).upper(),
                                                                                                            asmtSubject=param[Constants.ASMTSUBJECT].upper(),
                                                                                                            asmtType=param[Constants.ASMTTYPE].upper(),
                                                                                                            currentTime=str(datetime.now().strftime("%m-%d-%Y_%H-%M-%S")),
                                                                                                            asmtGuid=param[Constants.ASMTGUID])
    return os.path.join(get_extract_work_zone_path(tenant, request_id), file_name)


def get_asmt_metadata_file_path(params, tenant, request_id):
    return os.path.join(get_extract_work_zone_path(tenant, request_id), get_metadata_file_name(params))


def get_encryption_public_key_identifier(tenant):
    return get_current_registry().settings.get('extract.gpg.public_key.' + tenant)


def get_archive_file_path(user_name, tenant, request_id):
    base = _get_extract_work_zone_base_dir()
    file_name = '{user_name}_{current_time}.zip.gpg'.format(user_name=user_name, current_time=str(datetime.now().strftime("%m-%d-%Y_%H-%M-%S")))
    return os.path.join(base, tenant, request_id, 'zip', file_name)


def get_gatekeeper(tenant):
    '''
    Give a tenant name, return the path of gatekeeper's jail acct path

    :params string tenant:  name of tenant
    '''
    return get_current_registry().settings.get('pickup.gatekeeper.' + tenant)


def get_pickup_zone_info(tenant):
    '''
    Returns a tuple containing of sftp hostname, user, private key path
    '''
    reg = get_current_registry().settings
    server = reg.get('pickup.sftp.hostname', 'localhost')
    user = reg.get('pickup.sftp.user')
    private_key_path = reg.get('pickup.sftp.private_key_file')
    return (server, user, private_key_path)
