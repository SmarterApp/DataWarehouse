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
Created on Jul 15, 2014

@author: agrebneva
'''
import logging
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPServiceUnavailable, HTTPAccepted
from edapi.decorators import validate_xml
from smarter_score_batcher.utils import xsd
from pyramid.threadlocal import get_current_registry
from smarter_score_batcher.tasks.remote_file_writer import remote_write
from edapi.httpexceptions import EdApiHTTPPreconditionFailed
from smarter_score_batcher.error.exceptions import MetaNamesException


logger = logging.getLogger("smarter_score_batcher")
xsd_data = xsd.xsd.get_xsd() if xsd.xsd is not None else None


@view_config(route_name='xml', request_method='POST', content_type="application/xml", renderer='json')
@validate_xml(xsd_data)
def xml_catcher(xml_body):
    '''
    XML receiver service expects XML post and will delegate processing based on the root element.
    :param xml_body: xml data
    :returns: http response
    '''
    try:
        settings = get_current_registry().settings
        succeed = process_xml(settings, xml_body)
        if succeed:
            return HTTPAccepted()
        else:
            return HTTPServiceUnavailable("Writing XML file to disk failed.")
    except MetaNamesException as e:
        raise EdApiHTTPPreconditionFailed(str(e))
    except Exception as e:
        logger.error(str(e))
        raise


def process_xml(settings, raw_xml_string):
    '''
    Pre-Process XML (Save it to disk)
    :param meta_names: Meta object
    :param raw_xml_string: xml data
    :param root_dir_xml: xml root directory
    :param queue_name: celery sync queue name
    :param timeout: timeout in second for celery to get result
    :returns" celery response
    '''
    timeout = int(settings.get("smarter_score_batcher.celery_timeout", 30))
    queue_name = settings.get('smarter_score_batcher.sync_queue')
    celery_response = remote_write.apply_async(args=(raw_xml_string,), queue=queue_name)  # @UndefinedVariable
    # wait until file successfully written to disk
    return celery_response.get(timeout=timeout)
