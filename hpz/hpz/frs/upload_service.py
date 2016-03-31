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

"""
This module describes the file upload endpoint for HPZ.
"""
from hpz.frs.mail import sendmail
from hpz.database.constants import HPZ
__author__ = 'ablum,'
__author__ = 'tshewchuk'

import os
import shutil
import logging

from pyramid.response import Response
from pyramid.view import view_config

from hpz.database.file_registry import FileRegistry
from hpz.frs.decorators import validate_request_info
from urllib.parse import urljoin


logger = logging.getLogger(__name__)
FILE_NAME_HEADER = 'File-Name'
FILE_BODY_ATTRIBUTE = 'file'


@view_config(route_name='files', renderer='json', request_method='POST')
@validate_request_info('headers', FILE_NAME_HEADER)
@validate_request_info('POST', FILE_BODY_ATTRIBUTE)
def file_upload_service(context, request):
    registration_id = request.matchdict['registration_id']
    file_name = request.headers[FILE_NAME_HEADER]

    base_upload_path = request.registry.settings['hpz.frs.upload_base_path']
    file_size_limit = int(request.registry.settings['hpz.frs.file_size_limit'])
    file_pathname = os.path.join(base_upload_path, registration_id)

    try:
        if FileRegistry.is_file_registered(registration_id):

            input_file = request.POST['file'].file

            with open(file_pathname, mode='wb') as output_file:
                shutil.copyfileobj(input_file, output_file)

            if os.path.getsize(file_pathname) > file_size_limit:
                logger.warning('File %s exceeds recommended size limit', file_pathname)

            logger.info('File %s was successfully uploaded', file_pathname)
            FileRegistry.update_registration(registration_id, file_pathname, file_name)
            mail_server = request.registry.settings.get('hpz.mail.server')
            if mail_server is not None and mail_server != 'None':
                base_url = request.registry.settings.get('hpz.frs.download_base_url')
                mail_port = request.registry.settings.get('hpz.mail.port', 465)
                if type(mail_port) is str:
                    mail_port = int(mail_port)
                mail_from = request.registry.settings.get('hpz.mail.sender')
                mail_return_path = request.registry.settings.get('hpz.mail.return_path', mail_from)
                mail_subject = request.registry.settings.get('hpz.mail.subject')
                hpz_web_url = urljoin(base_url, '/download/' + registration_id)
                aws_mail_username = request.registry.settings.get('hpz.mail.smtp_username')
                aws_mail_password = request.registry.settings.get('hpz.mail.smtp_password')
                registration = FileRegistry.get_registration_info(registration_id)
                user_id = registration[HPZ.EMAIL]
                email = True
                try:
                    email = sendmail(mail_server, mail_port, mail_from, user_id, mail_return_path, mail_subject, hpz_web_url, aws_mail_username, aws_mail_password)
                except:
                    email = False
                if email is False:
                    logger.error('failed to sent email to ' + user_id)
        else:
            logger.error('The file attempting to be upload is not registered')
    except IOError as e:
        logger.error('Cannot complete file copying due to: %s' % str(e))

    return Response()
