# (c) 2014 The Regents of the University of California. All rights reserved,
# subject to the license below.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0. Unless required by
# applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

'''
Created on May 2, 2014

@author: nestep
'''
from pyramid.view import view_config
from edapi.logging import audit_event
from edapi.decorators import validate_params
from edapi.utils import convert_query_string_to_dict_arrays
from edextract.exceptions import ExtractionError
from edcore.utils.utils import merge_dict
from pyramid.response import Response
from edapi.httpexceptions import EdApiHTTPPreconditionFailed,\
    EdApiHTTPInternalServerError
import json
from smarter.reports.helpers.constants import AssessmentType, Constants
from smarter.extracts.student_asmt_processor import process_async_item_or_raw_extraction_request
from smarter.extracts.constants import ExtractType
from smarter.reports.helpers.filters import FILTERS_CONFIG
from datetime import datetime
import logging


logger = logging.getLogger('smarter')


ITEM_EXTRACT_PARAMS = {
    "type": "object",
    "additionalProperties": False,
    "properties": merge_dict({
        Constants.STATECODE: {
            "type": "string",
            "pattern": "^[a-zA-Z]{2}$",
            "required": True
        },
        Constants.ASMTYEAR: {
            "type": "string",
            "pattern": "^\d{4}$",
            "required": True
        },
        Constants.ASMTTYPE: {
            "type": "string",
            "pattern": "^(" + AssessmentType.SUMMATIVE + "|" + AssessmentType.INTERIM_COMPREHENSIVE + ")$",
            "required": True
        },
        Constants.ASMTSUBJECT: {
            "type": "string",
            "pattern": "^(" + Constants.MATH + "|" + Constants.ELA + ")$",
            "required": True
        },
        Constants.ASMTGRADE: {
            "type": "string",
            "pattern": "^[K0-9]+$",
            "maxLength": 2,
            "required": True,
        },
        Constants.ITEMID: {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^[a-zA-Z0-9\-]*$"
            },
            "minItems": 1,
            "uniqueItems": True,
            "required": False,
        }
    }, FILTERS_CONFIG)
}


@view_config(route_name='assessment_item_level', request_method='POST')
@validate_params(schema=ITEM_EXTRACT_PARAMS)
@audit_event()
def post_item_extract_service(context, request):
    '''
    Handles POST request to /services/extract/assessment_item_level

    :param request:  Pyramid request object
    '''
    params = {}
    for k, v in request.json_body.items():
        params[k] = v
    return send_extraction_request(params)


@view_config(route_name='assessment_item_level', request_method='GET')
@validate_params(schema=ITEM_EXTRACT_PARAMS)
@audit_event()
def get_item_extract_service(context, request):
    '''
    Handles GET request to /services/extract/assessment_item_level

    :param request:  Pyramid request object
    '''
    try:
        params = convert_query_string_to_dict_arrays(request.GET)
        params[Constants.STATECODE] = params[Constants.STATECODE][0]
        params[Constants.ASMTYEAR] = params[Constants.ASMTYEAR][0]
        params[Constants.ASMTTYPE] = params[Constants.ASMTTYPE][0]
        params[Constants.ASMTSUBJECT] = params[Constants.ASMTSUBJECT][0]
        params[Constants.ASMTGRADE] = params[Constants.ASMTGRADE][0]
    except Exception as e:
        logger.error("Item extract : pre-condition failed. %s", str(e))
        raise EdApiHTTPPreconditionFailed(e)
    return send_extraction_request(params)


def send_extraction_request(params):
    '''
    Requests for data extraction

    Sync and Async type are both processed here
    Sync calls return content type of 'application/octet-stream'
    Async calls return a json Response

    By default, it is a synchronous call unless otherwise specified

    :param session: session for this user request
    :param params: python dict that contains query parameters from the request
    '''
    response = None
    try:
        results = process_async_item_or_raw_extraction_request(params, extract_type=ExtractType.itemLevel)
        response = Response(body=json.dumps(results), content_type='application/json')
    # TODO: currently we dont' even throw any of these exceptions
    except ExtractionError as e:
        logger.error("Item extract : extraction failed. %s", str(e))
        raise EdApiHTTPInternalServerError(e.msg)
    except TimeoutError as e:
        # if celery timed out...
        logger.error("Item extract : timeout. %s", str(e))
        raise EdApiHTTPInternalServerError(e.msg)
    except Exception as e:
        # uknown exception was thrown.  Most likely configuration issue.
        logger.error("Item extract : Unknown exception. Check configuration. %s", str(e))
        raise
    return response


def generate_zip_file_name(params):
    '''
    Generate file name for archive file according
        Zip file name:

        ITEMS_<year>_<type>_<subject>_<grade>_<timestamp>.zip
    '''
    return "ITEMS_{stateCode}_{asmtYear}_{asmtType}_{asmtSubject}_GRADE_{asmtGrade}_{timestamp}.zip".\
        format(stateCode=params.get(Constants.STATECODE),
               asmtYear=params.get(Constants.ASMTYEAR),
               asmtType=params.get(Constants.ASMTTYPE).upper(),
               asmtSubject=params.get(Constants.ASMTSUBJECT).upper(),
               asmtGrade=params.get(Constants.ASMTGRADE).upper(),
               timestamp=datetime.now().strftime("%m-%d-%Y_%H-%M-%S"))
