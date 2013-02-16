'''
Created on Feb 13, 2013

@author: dip
'''
from pyramid.security import NO_PERMISSION_REQUIRED, forget, remember,\
    authenticated_userid, effective_principals
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.view import view_config, forbidden_view_config
from xml.dom.minidom import parseString
import base64
from edapi.saml2.saml_request import SamlAuthnRequest, SamlLogoutRequest
from edapi.saml2.saml_auth import SamlAuth
from edapi.saml2.saml_response import SAMLResponse
import urllib
from edapi.security.session_manager import create_new_user_session,\
    delete_session, get_user_session
from edapi.security.roles import Roles


# forbidden_view_config decorator indicates that this is the route to redirect to when an user
# has no access to a page
@view_config(route_name='login', permission=NO_PERMISSION_REQUIRED)
@forbidden_view_config(renderer='json')
def login(request):
    # TODO:  derive from configuration
    url = 'http://edwappsrv4.poc.dum.edwdc.net:18080/opensso/SSORedirect/metaAlias/idp?%s'

    # Both of these calls will trigger our callback
    session_id = authenticated_userid(request)
    principle = effective_principals(request)

    # Requests will be forwarded here when users aren't authorized to those pages, how to prevent it?
    # Here, we return 403 for users that has a role of None
    # This can be an user that has no role from IDP or has a role that we don't know of
    if Roles.NONE in principle:
        return HTTPForbidden()

    referrer = request.url
    if referrer == request.route_url('login') or referrer == request.route_url('logout'):
        # Never redirect back to login page or logout
        # TODO redirect to some landing home page
        referrer = request.route_url('list_of_reports')
    params = {'RelayState': request.params.get('came_from', referrer)}

    # clear out the session if we found one in the cookie
    if session_id is not None:
        delete_session(session_id)

    saml_request = SamlAuthnRequest()

    # combined saml_request into url params and url encode it
    params.update(saml_request.create_request())
    params = urllib.parse.urlencode(params)

    # Redirect to openam
    return HTTPFound(location=url % params)


@view_config(route_name='logout', permission=NO_PERMISSION_REQUIRED)
def logout(request):
    # Get the current session
    session_id = authenticated_userid(request)

    # Redirect to login if no session exist
    url = request.route_url('login')
    headers = None
    params = {}

    if session_id is not None:
        # remove cookie
        headers = forget(request)
        session = get_user_session(session_id)

        # Logout request to identity provider
        logout_request = SamlLogoutRequest(session.get_idp_session_index())
        params = logout_request.create_request()
        params = urllib.parse.urlencode(params)
        # TODO: derive from config
        url = 'http://edwappsrv4.poc.dum.edwdc.net:18080/opensso/IDPSloRedirect/metaAlias/idp?%s'

        # delete our session
        delete_session(session_id)

    return HTTPFound(location=url % params, headers=headers)


@view_config(route_name='saml2_post_consumer', permission=NO_PERMISSION_REQUIRED, request_method='POST')
def saml2_post_consumer(request):
    auth_request_id = "retrieve the id"

    # Validate the response id against session
    __SAMLResponse = base64.b64decode(request.POST['SAMLResponse'])
    __dom_SAMLResponse = parseString(__SAMLResponse.decode('utf-8'))

    response = SAMLResponse(__dom_SAMLResponse)
    saml_response = SamlAuth(response, auth_request_id=auth_request_id)
    if saml_response.is_validate():

        # create a session
        session_id = create_new_user_session(response).get_session_id()

        # Save session id to cookie
        headers = remember(request, session_id)

        # Get the url saved in RelayState from SAML request, redirect it back to it
        # If it's not found, redirect to list of reports
        # TODO: Need a landing other page
        redirect_url = request.POST.get('RelayState', request.route_url('list_of_reports'))
    else:
        redirect_url = request.route_url('login')
        headers = None
    return HTTPFound(location=redirect_url, headers=headers)
