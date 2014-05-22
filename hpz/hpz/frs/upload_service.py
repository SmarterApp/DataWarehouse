"""
This module describes the file upload endpoint for HPZ.
"""
__author__ = 'ablum,'
__author__ = 'tshewchuk'

import os
import shutil
import logging

from pyramid.response import Response
from pyramid.view import view_config

from hpz.database.file_registry import FileRegistry


logger = logging.getLogger(__name__)


@view_config(route_name='files', renderer='json', request_method='POST')
def file_upload_service(context, request):

    registration_id = request.matchdict['registration_id']
    file_ext = request.headers['Fileext']
    base_upload_path = request.registry.settings['hpz.frs.upload_base_path']
    file_size_limit = int(request.registry.settings['hpz.frs.file_size_limit'])
    file_pathname = os.path.join(base_upload_path, registration_id + '.' + file_ext)

    try:
        if FileRegistry.update_registration(registration_id, file_pathname):

            input_file = request.POST['file'].file

            with open(file_pathname, mode='wb') as output_file:
                shutil.copyfileobj(input_file, output_file)

            if os.path.getsize(file_pathname) > file_size_limit:
                logger.warning('File [%s] exceeds recommended size limit', file_pathname)

            logger.info('The file was successfully uploaded')

        else:
            logger.error('The file attempting to be upload is not registered')
    except IOError as e:
        logger.error('Cannot complete file copying due to: %s' % str(e))

    return Response()
