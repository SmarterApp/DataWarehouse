'''
Created on Nov 1, 2013

@author: ejen
'''
from pyramid.view import view_config
from pyramid.security import authenticated_userid
from edapi.logging import audit_event
from edapi.decorators import validate_params
from edapi.exceptions import InvalidParameterError, ForbiddenError
from edapi.utils import convert_query_string_to_dict_arrays
from edextract.exceptions import ExtractionError
from pyramid.response import Response
from edapi.httpexceptions import EdApiHTTPPreconditionFailed,\
    EdApiHTTPForbiddenAccess, EdApiHTTPInternalServerError
import json
from smarter.reports.helpers.constants import AssessmentType, Constants,\
    ExtractType
from smarter.extract.smarter_query import process_extraction_request

EXTRACT_PARAMS = {
    "type": "object",
    "properties": {
        'extractType': {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^" + ExtractType.studentAssessment + "$"
            },
            "minItems": 1,
            "uniqueItems": True
        },
        'asmtType': {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^(" + AssessmentType.SUMMATIVE + "|" + AssessmentType.COMPREHENSIVE_INTERIM + ")$"
            },
            "minItems": 1,
            "uniqueItems": True
        },
        'asmtSubject': {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^(" + Constants.MATH + "|" + Constants.ELA + ")$"
            },
            "minItems": 1,
            "uniqueItems": True
        },
        'asmtYear': {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^\d{4}$"
            },
            "minItems": 1,
            "uniqueItems": True
        },
        'stateCode': {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^[a-zA-Z]{2}$"
            },
            "minItems": 1,
            "uniqueItems": True
        },
        'sl': {  # this is added by GET request inside browsers
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^\d+$"
            },
            "required": False
        }
    },
    "required": ["extractType", "asmtSubject", "asmtType", "asmtYear", "stateCode"]
}


@view_config(route_name='extract', request_method='POST', content_type='application/json')
@validate_params(method='POST', schema=EXTRACT_PARAMS)
#@audit_event()
def post_extract_service(context, request):
    '''
    Handles POST request to /services/extract

    :param request:  Pyramid request object
    '''
    try:
        params = request.json_body
        user = authenticated_userid(request)
    except ValueError:
        raise EdApiHTTPPreconditionFailed('Payload cannot be parsed')
    except Exception as e:
        raise EdApiHTTPPreconditionFailed(e)
    return send_extraction_request(user, params)


@view_config(route_name='extract', request_method='GET')
@validate_params(method='GET', schema=EXTRACT_PARAMS)
#@audit_event()
def get_extract_service(context, request):
    '''
    Handles GET request to /services/extract

    :param request:  Pyramid request object
    '''
    try:
        user = authenticated_userid(request)
        params = convert_query_string_to_dict_arrays(request.GET)
    except ValueError:
        raise EdApiHTTPPreconditionFailed('Payload cannot be parsed')
    except Exception as e:
        raise EdApiHTTPPreconditionFailed(e)
    return send_extraction_request(user, params)


def send_extraction_request(session, params):
    '''
    Requests for data extraction, throws http exceptions when error occurs

    :param session: session for this user reqest
    :param params: python dict that contains query parameters from the request
    '''
    try:
        results = process_extraction_request(session, params)
        return Response(body=json.dumps(results), content_type='application/json')
    # TODO: currently we dont' even throw any of these exceptions
    except InvalidParameterError as e:
        raise EdApiHTTPPreconditionFailed(e.msg)
    except ForbiddenError as e:
        raise EdApiHTTPForbiddenAccess(e.msg)
    except ExtractionError as e:
        raise EdApiHTTPInternalServerError(e.msg)
    except TimeoutError as e:
        # if celery get task got timed out...
        raise EdApiHTTPInternalServerError(e.msg)
