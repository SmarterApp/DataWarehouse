'''
Created on May 17, 2013

@author: dip
'''
from pyramid.view import view_config
#from services.tasks.pdf import get
from urllib.parse import urljoin
from pyramid.response import Response
from smarter.security.context import check_context
from edapi.exceptions import InvalidParameterError, ForbiddenError
from edauth.security.utils import get_session_cookie
import urllib.parse
import pyramid.threadlocal
from edapi.httpexceptions import EdApiHTTPPreconditionFailed, \
    EdApiHTTPForbiddenAccess, EdApiHTTPInternalServerError, EdApiHTTPNotFound
#from services.exceptions import PdfGenerationError
#from smarter.reports.helpers.ISR_pdf_name_formatter import generate_isr_report_path_by_student_guid
from smarter.reports.helpers.constants import AssessmentType
#import services.celeryconfig
from edauth.utils import to_bool


@view_config(route_name='extract', request_method='POST', content_type='application/json')
def post_extract_service(request):
    '''
    Handles POST request to /services/extract

    :param request:  Pyramid request object
    '''
    try:
        params = request.json_body
    except ValueError:
        raise EdApiHTTPPreconditionFailed('Payload cannot be parsed')

    return send_extraction_request(params)


@view_config(route_name='extract', request_method='GET')
def get_extract_service(request):
    '''
    Handles GET request to /services/extract

    :param request:  Pyramid request object
    '''
    return send_extraction_request(request.GET)


def send_extraction_request(params):
    '''
    Requests for data extraction, throws http exceptions when error occurs

    :param params: python dict that contains query parameters from the request
    '''
    print(params)
    #report = pyramid.threadlocal.get_current_request().matchdict['report'].lower()
    #if report not in KNOWN_REPORTS:
    #    raise EdApiHTTPNotFound("Not Found")

    #try:
    #    response = get_pdf_content(params)
    #except InvalidParameterError as e:
    #    raise EdApiHTTPPreconditionFailed(e.msg)
    #except ForbiddenError as e:
    #    raise EdApiHTTPForbiddenAccess(e.msg)
    #except PdfGenerationError as e:
    #    raise EdApiHTTPInternalServerError(e.msg)
    #except TimeoutError as e:
        # if celery get task got timed out...
    #    raise EdApiHTTPInternalServerError(e.msg)
    response = Response(body='here', content_type='text/plain')
    return response
