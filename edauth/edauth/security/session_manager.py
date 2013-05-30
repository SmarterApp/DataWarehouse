'''
Created on Feb 14, 2013

@author: tosako
'''
from datetime import datetime, timedelta
import uuid
import re
from edauth.security.session import Session
from edauth.security.roles import Roles
from edauth.database.connector import EdauthDBConnection
import socket
import logging
from edauth.security.session_backend import get_session_backend

# TODO: remove datetime.now() and use func.now()

logger = logging.getLogger('edauth')


def get_user_session(session_id):
    '''
    get user session from DB
    if user session does not exist, then return None
    '''
    return get_session_backend().get_session(session_id)


def write_security_event(message_content, message_type):
    '''
    Write a security event details to a table in DB
    '''
    with EdauthDBConnection() as connection:
        security_events = connection.get_table('security_event')
        # store the security event into DB
        connection.execute(security_events.insert(), message=message_content, type=message_type, host=socket.gethostname())


def create_new_user_session(saml_response, session_expire_after_in_secs=30):
    '''
    Create new user session from SAMLResponse
    '''
    # current local time
    current_datetime = datetime.now()
    # How long session lasts
    expiration_datetime = current_datetime + timedelta(seconds=session_expire_after_in_secs)
    # create session SAML Response
    session = __create_from_SAMLResponse(saml_response, current_datetime, expiration_datetime)
    session.set_expiration(expiration_datetime)
    session.set_last_access(current_datetime)

    get_session_backend().create_new_session(session)

    return session


def update_session_access(session):
    '''
    update user_session.last_access
    '''
    current_time = datetime.now()
    session.set_last_access(current_time)

    get_session_backend().update_last_access_time(session)


def expire_session(session_id):
    '''
    expire session by session_id
    '''
    get_session_backend().delete_session(session_id)


def __create_from_SAMLResponse(saml_response, last_access, expiration):
    '''
    populate session from SAMLResponse
    '''
    # make a UUID based on the host ID and current time
    __session_id = str(uuid.uuid4())

    # get Attributes
    __assertion = saml_response.get_assertion()
    __attributes = __assertion.get_attributes()
    __name_id = __assertion.get_name_id()
    session = Session()
    session.set_session_id(__session_id)
    # get fullName
    fullName = __attributes.get('fullName')
    if fullName is not None:
        session.set_fullName(fullName[0])

    # get firstName
    firstName = __attributes.get('firstName')
    if firstName is not None:
        session.set_firstName(firstName[0])

    # get lastName
    lastName = __attributes.get('lastName')
    if lastName is not None:
        session.set_lastName(lastName[0])

    # get uid
    if 'uid' in __attributes:
        if __attributes['uid']:
            session.set_uid(__attributes['uid'][0])
    # get roles
    session.set_roles(__get_roles(__attributes))
    # set nameId
    session.set_name_id(__name_id)

    session.set_expiration(expiration)
    session.set_last_access(last_access)

    # get auth response session index that identifies the session with identity provider
    session.set_idp_session_index(__assertion.get_session_index())

    return session


def is_session_expired(session):
    '''
    check if current session is expired or not
    '''
    is_expire = datetime.now() > session.get_expiration()
    return is_expire


def __get_roles(attributes):
    '''
    find roles from Attributes Element (SAMLResponse)
    '''
    roles = []
    values = attributes.get("memberOf", None)
    if values is not None:
        for value in values:
            cn = re.search('cn=(.*?),', value.lower())
            if cn is not None:
                role = cn.group(1).upper()
                roles.append(role)
    # If user has no roles or has a role that is not defined
    if not roles or Roles.has_undefined_roles(roles):
        roles.append(Roles.get_invalid_role())
    return roles


def cleanup_sessions():
    with EdauthDBConnection() as connection:
        user_session = connection.get_table('user_session')
        connection.execute(user_session.delete())
