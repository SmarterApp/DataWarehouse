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
Created on Feb 13, 2013

@author: dip
'''
from pyramid.security import NO_PERMISSION_REQUIRED, forget, remember, \
    effective_principals, unauthenticated_userid
from pyramid.httpexceptions import HTTPFound, HTTPMovedPermanently, \
    HTTPForbidden, HTTPUnauthorized, HTTPError
from pyramid.view import view_config, forbidden_view_config
import base64
from edauth.saml2.saml_request import SamlAuthnRequest, SamlLogoutRequest
import urllib
from edauth.security.session_manager import get_user_session, \
    expire_session, create_session
from edauth.utils import convert_to_int
from pyramid.response import Response
from edauth.security.roles import Roles
from edauth.saml2.saml_response_manager import SAMLResponseManager
from edauth.saml2.saml_idp_metadata_manager import IDP_metadata_manager
from urllib.parse import parse_qs, urlsplit, urlunsplit
from edauth.security.utils import _get_cipher, load_class
from datetime import datetime
import json
import pyramid.security
from edauth.security.exceptions import NotAuthorized
from edauth.security.logging import SECURITY_EVENT_TYPE, write_security_event
from requests.api import get
import re


@forbidden_view_config()
@view_config(route_name='login', permission=NO_PERMISSION_REQUIRED)
def login(request):
    '''
    forbidden_view_config decorator indicates that this is the route to redirect to when an user
    has no access to a page
    '''

    # Get session id from cookie
    session_id = unauthenticated_userid(request)
    # Get roles
    principals = effective_principals(request)

    # Requests will be forwarded here when users aren't authorized to those pages
    # If they are unauthorized to those pages, they should have session id and principals
    # and, if there is a session id and principals, return 403
    # Here, we return 403 for users that has a role of None
    # This can be an user that has no role from IDP or has a role that we don't know of
    if Roles.get_invalid_role() in principals or (principals and session_id):
        write_security_event("Forbidden view being accessed", SECURITY_EVENT_TYPE.WARN, session_id)
        return HTTPForbidden()

    # clear out the session if we found one in the cookie
    if session_id is not None:
        expire_session(session_id)

    handlers = [_handle_OAUTH2_Implicit_login_flow, _handle_SAML2_login_flow]
    for handler in handlers:
        response = handler(request)
        if response is not None:
            return response

    return HTTPForbidden()


def _get_user_destination(request):
    '''
    Get original user requested URL or a default location
    @param request: current request
    '''
    if request.is_xhr:
        # If it's a xhr request, use the referrer URL
        referrer = request.referrer
    else:
        referrer = request.url

    if referrer == request.route_url('login'):
        # Never redirect back to login page
        referrer = request.route_url('list_of_reports')

    return referrer


def _handle_OAUTH2_Implicit_login_flow(request):
    '''
    This call is to check for oauth2 flow. It checks if bearer is present and checks with IdP
    if valid
    '''
    auth_header = request.headers.get("Authorization", None)
    if auth_header is not None:
        m = re.match(r"Bearer ([\w-]+)", auth_header, re.I)
        bearer = m.group(1)
        if bearer is None:
            return
        verify_url = request.registry.settings['auth.oauth2.idp_server_verify_url']
        timeout = request.registry.settings.get('auth.oauth2.idp_server_verify_url.timeout', 10)
        headers = {"Content-Type": "application/x-www-form-urlenocded"}
        identity_parser_class = load_class(request.registry.settings.get('auth.oauth2.identity_parser', 'edauth.security.basic_identity_parser.BasicIdentityParser'))
        try:
            response = get(verify_url, params={"access_token": bearer}, timeout=timeout, headers=headers)
            response.raise_for_status()
            session_id = create_session(request, response.json(), None, None, identity_parser_class)
        except Exception as _:
            write_security_event("OAuth verification failed with exception {exception}".format(exception=_), SECURITY_EVENT_TYPE.WARN)
            return HTTPUnauthorized(body=json.dumps({'Error': 'User Validation Fails'}), content_type='application/json')
        session_headers = remember(request, session_id)
        write_security_event("Login processed successfully", SECURITY_EVENT_TYPE.INFO, session_id=session_id)
        headers = session_headers.copy()
        headers.extend(list(request.headers.items()))
        # we are forwarding the request so we need good auth cookies instead of set-cookie
        cookies = [('Cookie', header[1]) for header in headers if header[0] == 'Set-Cookie']
        headers.extend(cookies)
        subreq = request.copy()
        subreq.headers = headers
        res = request.invoke_subrequest(subreq, use_tweens=True)
        # add set-cookie headers to response
        res.headerlist.extend(session_headers)
        return res


def _handle_SAML2_login_flow(request):
    url = request.registry.settings['auth.saml.idp_server_login_url']
    # TODO:  This doesn't handle POST requests
    # Split the url to read query params for saml_login
    split_url = urlsplit(_get_user_destination(request))
    query_params = parse_qs(split_url.query, keep_blank_values=True)
    last_saml_time = query_params.get('sl')
    current_time = datetime.now().strftime('%s')

    if last_saml_time and len(last_saml_time) > 0:
        last_access = 0
        for saml_try in last_saml_time:
            saml_try = convert_to_int(saml_try)
            if saml_try and saml_try > last_access:
                last_access = saml_try
                message = "TEST EDAUTH VIEW: _handle_SAML2_login_flow, saml_try: {0}".format(str(saml_try))
                write_security_event(message, SECURITY_EVENT_TYPE.INFO)

        # Protect ourselves from infinite loop
        duration = int(current_time) - last_access
        if duration < 3:
            write_security_event("Unauthorized Request.", SECURITY_EVENT_TYPE.INFO)
            raise NotAuthorized()

    query_params['sl'] = current_time
    # rebuild url
    url_query_params = urllib.parse.urlencode(query_params, doseq=True)
    new_url = (split_url[0], split_url[1], split_url[2], url_query_params, split_url[4])
    referrer = urlunsplit(new_url)
    params = {'RelayState': _get_cipher().encrypt(referrer)}

    saml_request = SamlAuthnRequest(request.registry.settings['auth.saml.issuer_name'])

    # combined saml_request into url params and url encode it
    params.update(saml_request.generate_saml_request())
    params = urllib.parse.urlencode(params)

    redirect_url = url + "?%s" % params

    # Redirect to sso if it's not an ajax call, and if we detected that the requested url is different than referrer
    # This is a patch to get around api calls made from browser window.location
    if not request.is_xhr and request.referrer is not None and request.url != request.referrer:
        write_security_event("Redirect to Idp", SECURITY_EVENT_TYPE.INFO)
        return HTTPFound(location=redirect_url)

    # We need to return 401 with a redirect url and the front end will handle the redirect
    write_security_event("Unauthorized Request. redirect to Idp", SECURITY_EVENT_TYPE.INFO)
    return HTTPUnauthorized(body=json.dumps({'redirect': redirect_url}), content_type='application/json')


def _get_landing_page(request, redirect_url_decoded, headers):
    '''
    Login callback for redirect
    This is a blank page with redireect to the requested resource page.
    To prevent from a user from clicking back botton to OpenAM login page
    '''
    html = '''
    <html><head>
    <title>Processing</title>
    <META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-CACHE">
    <META HTTP-EQUIV="PRAGMA" CONTENT="NO-CACHE">
    <META HTTP-EQUIV="Expires" CONTENT="0">
    <meta http-equiv="refresh" content="0;url=%s">
    <script type="text/javascript">
        function redirect() {
        document.getElementById('url').click()
        }
    </script>
    </head>
    <body onload="redirect()"><a href="%s" id=url onclick="javascript:location.replace('%s'); event.returnValue=false;"></a></body></html>
    ''' % (redirect_url_decoded, redirect_url_decoded, redirect_url_decoded)
    headers.append(('Content-Type', 'text/html'))
    return Response(body=html, headers=headers, content_type='text/html')


@view_config(route_name='logout', permission='logout')
def logout(request):
    # Get the current session
    session_id = unauthenticated_userid(request)

    # Redirect to login if no session exist
    url = request.route_url('login')
    headers = None
    params = {}

    if session_id is not None:
        # remove cookie
        headers = forget(request)
        session = get_user_session(session_id)

        # Check that there is a session in db, else we can't log out from IDP
        # If for some reason, we get into this case where session is not found in db, it'll redirect back to login route
        # and if the user still has a valid session with IDP, it'll redirect to default landing page
        if session is not None:
            # Logout request to identity provider
            logout_request = SamlLogoutRequest(request.registry.settings['auth.saml.issuer_name'],
                                               session.get_idp_session_index(),
                                               request.registry.settings['auth.saml.name_qualifier'],
                                               session.get_name_id())
            params = logout_request.generate_saml_request()
            params = urllib.parse.urlencode(params)
            url = request.registry.settings['auth.saml.idp_server_logout_url'] + "?%s" % params

            write_security_event("Logout requested", SECURITY_EVENT_TYPE.INFO, session_id)
            # expire our session
            expire_session(session_id)

    return HTTPFound(location=url, headers=headers)


@view_config(route_name='saml2_post_consumer', permission=NO_PERMISSION_REQUIRED, request_method='POST')
def saml2_post_consumer(request):
    '''
    This is the postback from IDP
    '''
    # TODO: compare with auth response id
    auth_request_id = "retrieve the id"

    # Validate the response id against session
    __SAMLResponse = base64.b64decode(request.POST['SAMLResponse'])
    __SAMLResponse_manager = SAMLResponseManager(__SAMLResponse.decode('utf-8'))
    __SAMLResponse_IDP_Metadata_manager = IDP_metadata_manager(request.registry.settings['auth.idp.metadata'])

    __skip_verification = request.registry.settings.get('auth.skip.verify', False)
    # TODO: enable auth_request_id
    # if __SAMLResponse_manager.is_auth_request_id_ok(auth_request_id)
    condition = __SAMLResponse_manager.is_condition_ok()
    status = __SAMLResponse_manager.is_status_ok()
    signature = __SAMLResponse_manager.is_signature_ok(__SAMLResponse_IDP_Metadata_manager.get_trusted_pem_filename())

    if condition and status and (__skip_verification or signature):

        # create a session
        identity_parser_class = load_class(request.registry.settings.get('auth.saml.identity_parser', 'edauth.security.basic_identity_parser.BasicIdentityParser'))
        saml = __SAMLResponse_manager.get_SAMLResponse()
        assertion = saml.get_assertion()
        session_id = create_session(request, assertion.get_attributes(), assertion.get_name_id(), assertion.get_session_index(), identity_parser_class)

        # Save session id to cookie
        headers = remember(request, session_id)
        # Get the url saved in RelayState from SAML request, redirect it back to it
        # If it's not found, redirect to list of reports
        # TODO: Need a landing other page
        redirect_url = request.POST.get('RelayState')
        if redirect_url:
            redirect_url = _get_cipher().decrypt(redirect_url)
        else:
            redirect_url = request.route_url('list_of_reports')
        message = "TEST EDAUTH VIEW: saml2_post_consumer, redirect_url : {0}".format(str(redirect_url))
        write_security_event(message, SECURITY_EVENT_TYPE.INFO)

    else:
        message = "SAML response failed with Condition: {0}, Status: {1}, Signature: {2}".format(str(condition), str(status), str(signature))
        write_security_event(message, SECURITY_EVENT_TYPE.WARN)
        redirect_url = request.route_url('login')
        headers = []

    return _get_landing_page(request, redirect_url, headers=headers)


@view_config(route_name='logout_redirect', permission=NO_PERMISSION_REQUIRED)
def logout_redirect(request):
    '''
    OpenAM redirects back to this endpoint after logout
    This will refresh the whole page from the iframe
    '''
    html = '''
    <html><head>
    <title>Logging out</title>
    <script type="text/javascript">
    function refresh() {
        window.top.location.reload();
        }
    </script>
    </head>
    <body onload="refresh()">
    </body>
    </html>
    '''
    return Response(body=html, content_type='text/html')


@view_config(context=HTTPError, permission=pyramid.security.NO_PERMISSION_REQUIRED)
def error_handler(request):
    '''
    All 4xx-5xx get redirected
    '''
    return error_redirect(request)


@view_config(context=Exception, permission=pyramid.security.NO_PERMISSION_REQUIRED)
def error_handler_catchall_exc(request):
    '''
    All exceptions gets redirected here
    '''
    return error_redirect(request)


def error_redirect(request):
    '''
    Errors get redirected here
    '''
    return HTTPMovedPermanently(location=request.route_url('error'), expires=0, cache_control='no-store, no-cache, must-revalidate')
