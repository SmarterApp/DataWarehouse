# (c) 2014 Amplify Education, Inc. All rights reserved, subject to the license
# below.
#
# Education agencies that are members of the Smarter Balanced Assessment
# Consortium as of August 1, 2014 are granted a worldwide, non-exclusive, fully
# paid-up, royalty-free, perpetual license, to access, use, execute, reproduce,
# display, distribute, perform and create derivative works of the software
# included in the Reporting Platform, including the source code to such software.
# This license includes the right to grant sublicenses by such consortium members
# to third party vendors solely for the purpose of performing services on behalf
# of such consortium member educational agencies.

'''
Created on Feb 14, 2013

@author: tosako
'''
from datetime import datetime, timedelta
from edauth.security.session_backend import get_session_backend
from edauth.utils import convert_to_int
from edauth.security.exceptions import NotAuthorized
import logging

# TODO: remove datetime.now() and use func.now()
logger = logging.getLogger('edauth')

def create_session(request, user_info_response, name_id, session_index, identity_parser_class):
    session_timeout = convert_to_int(request.registry.settings['auth.session.timeout'])
    session_id = create_new_user_session(user_info_response, name_id, session_index, identity_parser_class, session_timeout).get_session_id()

    session = get_user_session(session_id)
    if not session:
        logger.info('TEST SESSION MGR: get_user_session, session not found for %s' % (session_id,))
        raise NotAuthorized()

    # If user doesn't have a Tenant, return 403
    if session.get_tenants() is None:
        logger.info('TEST SESSION MGR: get_user_session, session_id.get_tenants is None')
        raise NotAuthorized()

    return session_id


def get_user_session(session_id):
    '''
    get user session from DB
    if user session does not exist, then return None
    '''
    message = "TEST SESSION MGR: get_user_session, session_id: {0}".format(str(session_id))
    logger.info(message)
    return get_session_backend().get_session(session_id)


def create_new_user_session(user_info_response, name_id, session_index, identity_parser_class, session_expire_after_in_secs=30):
    '''
    Create new user session from SAMLResponse
    '''
    # current local time
    current_datetime = datetime.now()
    # How long session lasts
    expiration_datetime = current_datetime + timedelta(seconds=session_expire_after_in_secs)
    # create session
    session = identity_parser_class.create_session(name_id, session_index, user_info_response, current_datetime, expiration_datetime)
    session.set_expiration(expiration_datetime)
    session.set_last_access(current_datetime)

    get_session_backend().create_new_session(session)

    logger.info('TEST SESSION MGR: create_new_user_session, %r' % (session,))
    return session


def update_session_access(session):
    '''
    update_session user_session.last_access
    '''
    current_time = datetime.now()
    session.set_last_access(current_time)

    get_session_backend().update_session(session)
    logger.info('TEST SESSION MGR: update_session_access, %r' % (session,))


def expire_session(session_id):
    '''
    expire session by session_id
    '''
    session = get_user_session(session_id)
    current_time = datetime.now()
    message = "TEST SESSION MGR: expire_session, session_id: {0}".format(str(session_id))
    logger.info(message)
    if session is not None:
        # Expire the entry
        session.set_expiration(current_time)
        __backend = get_session_backend()
        __backend.update_session(session)
        # Delete the session
        __backend.delete_session(session_id)


def is_session_expired(session):
    '''
    check if current session is expired or not
    '''
    is_expire = datetime.now() > session.get_expiration()
    return is_expire
