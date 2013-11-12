'''
Celery Tasks for data extraction

Created on Nov 5, 2013

@author: ejen
'''
import logging
from smarter.reports.helpers.constants import Constants
from smarter.extract.constants import Constants as Extract
from edcore.database.edcore_connector import EdCoreDBConnection
from smarter.extract.student_assessment import get_extract_assessment_query
from pyramid.security import authenticated_userid
from uuid import uuid4
from edextract.status.status import create_new_entry
from edextract.tasks.extract import start_extract
from pyramid.threadlocal import get_current_request, get_current_registry
from datetime import datetime
import os


log = logging.getLogger('smarter')


def process_extraction_request(params):
    '''
    :param dict params: contains query parameter.  Value for each pair is expected to be a list
    '''
    tasks = []
    response = {}
    task_responses = []
    # Generate an uuid for this extract request
    request_id = str(uuid4())
    user = authenticated_userid(get_current_request())
    tenant = user.get_tenant()

    for e in params[Extract.EXTRACTTYPE]:
        for s in params[Constants.ASMTSUBJECT]:
            for t in params[Constants.ASMTTYPE]:
                # TODO: handle year and stateCode/tenant
                param = ({Extract.EXTRACTTYPE: e,
                         Constants.ASMTSUBJECT: s,
                         Constants.ASMTTYPE: t,
                         Constants.ASMTYEAR: params[Constants.ASMTYEAR][0],
                         Constants.STATECODE: params[Constants.STATECODE][0]})

                task_response = {Constants.STATECODE: param[Constants.STATECODE],
                                 Extract.EXTRACTTYPE: param[Extract.EXTRACTTYPE],
                                 Constants.ASMTSUBJECT: param[Constants.ASMTSUBJECT],
                                 Constants.ASMTTYPE: param[Constants.ASMTTYPE],
                                 #Constants.ASMTYEAR: task[Constants.ASMTYEAR],
                                 Extract.REQUESTID: request_id}

                check_query = get_extract_assessment_query(param, limit=1)

                if has_data(check_query, request_id):
                    extract_query = get_extract_assessment_query(param, compiled=True)
                    task = {}
                    task['task_id'] = create_new_entry(user, request_id, param)
                    task['file_name'] = get_file_path(param, tenant, request_id)
                    task['query'] = extract_query
                    tasks.append(task)
                    task_response[Extract.STATUS] = Extract.OK
                else:
                    task_response[Extract.STATUS] = Extract.FAIL
                    task_response[Extract.MESSAGE] = "Data is not available"
                task_responses.append(task_response)

    response['tasks'] = task_responses
    if len(tasks) > 0:
        # TODO: handle empty public key
        public_key_id = get_encryption_public_key_identifier(tenant)
        archive_file_name = get_archive_file_path(user.get_uid(), tenant, request_id)
        response['fileName'] = os.path.basename(archive_file_name)
        directory_to_archive = get_extract_work_zone_path(tenant, request_id)
        gatekeeper_id = get_gatekeeper(tenant)
        pickup_zone_info = get_pickup_zone_info(tenant)
        start_extract.apply_async(args=[tenant, request_id, public_key_id, archive_file_name, directory_to_archive, gatekeeper_id, pickup_zone_info, tasks], queue='extract')     # @UndefinedVariable
    return response


def has_data(query, request_id):
    log.info('Extract: data availability check for request ' + request_id)
    with EdCoreDBConnection() as connection:
        result = connection.get_result(query)
    if result is None or len(result) < 1:
        return False
    else:
        return True


def __get_extract_work_zone_base_dir():
    return get_current_registry().settings.get('extract.work_zone_base_dir', '/tmp')


def get_extract_work_zone_path(tenant, request_id):
    base = __get_extract_work_zone_base_dir()
    return os.path.join(base, tenant, request_id, 'csv')


def get_file_path(param, tenant, request_id):
    file_name = 'ASMT_{stateCode}_{asmtSubject}_{asmtType}_{currentTime}.csv.gpg'.format(stateCode=param[Constants.STATECODE].upper(),
                                                                                         asmtSubject=param[Constants.ASMTSUBJECT].upper(),
                                                                                         asmtType=param[Constants.ASMTTYPE].upper(),
                                                                                         currentTime=str(datetime.now().strftime("%m-%d-%Y_%H-%M-%S")))
    return os.path.join(get_extract_work_zone_path(tenant, request_id), file_name)


def get_encryption_public_key_identifier(tenant):
    return get_current_registry().settings.get('extract.gpg.public_key.' + tenant)


def get_archive_file_path(user_name, tenant, request_id):
    base = __get_extract_work_zone_base_dir()
    file_name = '{user_name}_{current_time}.zip'.format(user_name=user_name, current_time=str(datetime.now().strftime("%m-%d-%Y_%H-%M-%S")))
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