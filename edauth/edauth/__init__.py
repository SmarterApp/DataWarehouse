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
This is the top-level package for EdAuth.

'''
from pyramid.authorization import ACLAuthorizationPolicy
from edauth.security.callback import session_check
from edauth.utils import convert_to_int
from edauth.security.roles import Roles
from edschema.database.generic_connector import setup_db_connection_from_ini
from edauth.security.policy import EdAuthAuthenticationPolicy
from edauth.security.utils import AESCipher, ICipher
from zope import component
import logging
from apscheduler.scheduler import Scheduler
from edauth.security.session_backend import ISessionBackend, SessionBackend
from edcore.utils.utils import to_bool
import os


logger = logging.getLogger(__name__)


def includeme(config):
    '''
    Performs initialization tasks, such as setting configuration options.
    It is automatically called by a consumer of edauth when it calls config.include(edauth).
    '''
    settings = config.get_settings()

    setting_prefix = 'auth.policy.'
    options = dict((key[len(setting_prefix):], settings[key]) for key in settings if key.startswith(setting_prefix))

    for item, type_ in (
        ('timeout', int),
        ('secure', to_bool),
        ('include_ip', to_bool),
        ('reissue_time', int),
        ('wild_domain', to_bool),
        ('max_age', int),
        ('http_only', to_bool),
        ('debug', to_bool),
    ):
        if item in options.keys():
            options[item] = type_(options[item].lower())

    authentication_policy = EdAuthAuthenticationPolicy(callback=session_check, **options)

    authorization_policy = ACLAuthorizationPolicy()

    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)

    component.provideUtility(AESCipher(settings['auth.state.secret']), ICipher)

    component.provideUtility(SessionBackend(settings), ISessionBackend)

    # TODO: clean up and derive from ini?
    config.add_route('login', '/login')
    config.add_route('login_callback', '/login_callback')
    config.add_route('logout', '/logout')
    config.add_route('saml2_post_consumer', '/saml_post')
    config.add_route('logout_redirect', '/logout_redirect')

    # scans edauth, ignoring test package
    config.scan(ignore='edauth.test')


def set_roles(roles):
    '''
    Sets the list of known roles for authentication. Roles is a list of tuples.
    '''
    Roles.set_roles(roles)


def configure(settings):
    auth_idp_metadata = settings.get('auth.idp.metadata', None)
    if auth_idp_metadata is not None:
        if auth_idp_metadata.startswith('../'):
            settings['auth.idp.metadata'] = os.path.abspath(os.path.join(os.path.dirname(__file__), auth_idp_metadata))
