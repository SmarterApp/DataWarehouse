'''
Created on May 7, 2013

@author: dip
'''
from functools import wraps
from sqlalchemy.sql.expression import Select
from pyramid.security import authenticated_userid
import pyramid
from pyramid.httpexceptions import HTTPForbidden
from smarter.reports.helpers.constants import Constants
from smarter.security.context_role_map import ContextRoleMap
from edcore.database.edcore_connector import EdCoreDBConnection
from edcore.security.tenant import get_tenant_by_state_code
from smarter_common.security.constants import RolesConstants


def select_with_context(columns=None, whereclause=None, from_obj=[], permission=RolesConstants.PII, **kwargs):
    '''
    Returns a SELECT clause statement with context security attached in the WHERE clause

    Note: state_code must be passed in as kwargs for database routing for multi tenant users
    '''
    # Retrieve state code for db connection routing
    state_code = kwargs.get(Constants.STATE_CODE)
    kwargs.pop(Constants.STATE_CODE, None)
    with EdCoreDBConnection(state_code=state_code) as connector:
        # Get user role and guid
        user = __get_user_info()

        # Build query
        query = Select(columns, whereclause=whereclause, from_obj=from_obj, **kwargs)

        if permission not in user.get_roles():
            raise HTTPForbidden()
        context = __get_context_instance(permission, connector)
        # Get context security expression to attach to where clause
        query = context.add_context(get_tenant_by_state_code(state_code), user, query)

    return query


def check_context(permission, state_code, student_guids):
    '''
    Given a list of student guids, return true if user has access to see their data, false otherwise

    :param student_guids: guids of students that we want to check whether the user has context to
    :type student_guids: list
    '''
    if len(student_guids) is 0:
        return False

    with EdCoreDBConnection(state_code=state_code) as connector:
        # Get user role and guid
        user = __get_user_info()
        context = __get_context_instance(permission, connector)
        return context.check_context(get_tenant_by_state_code(state_code), user, student_guids)


def get_current_context(params):
    '''
    Given request parameters, determine if the user has context to the next hierarchy level
    '''
    user = __get_user_info()
    state_code = params.get(Constants.STATECODE)
    tenant = get_tenant_by_state_code(state_code)
    user_context = user.get_context()
    # Special case for pii
    pii = user_context.get_chain(tenant, RolesConstants.PII, params) if params.get(Constants.SCHOOLGUID) else {'all': True}
    sar_extracts = user_context.get_chain(tenant, RolesConstants.SAR_EXTRACTS, params)
    srs_extracts = user_context.get_chain(tenant, RolesConstants.SRS_EXTRACTS, params)
    src_extracts = user_context.get_chain(tenant, RolesConstants.SRC_EXTRACTS, params)
    return {'pii': pii, 'sar_extracts': sar_extracts, 'srs_extracts': srs_extracts, 'src_extracts': src_extracts}


def get_current_request_context(origin_func):
    '''
    Decorator to return current user context
    '''
    @wraps(origin_func)
    def wrap(*args, **kwds):
        results = origin_func(*args, **kwds)
        if results:
            results['context']['permissions'] = get_current_context(*args)
        return results
    return wrap


def __get_user_info():
    '''
    Returns user object.  This is not the session object

    '''
    return authenticated_userid(pyramid.threadlocal.get_current_request())


def __get_context_instance(role, connector):
    '''
    Given a role in string, return the context instance for it
    '''
    # Get the context object
    context_obj = ContextRoleMap.get_context(role)
    # Instantiate it
    return context_obj(connector, role)
