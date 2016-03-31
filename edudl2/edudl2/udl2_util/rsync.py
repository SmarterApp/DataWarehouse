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
Created on Aug 14, 2014

@author: tosako
'''
import subprocess
import logging
import tempfile
import os
import shutil
from edudl2.udl2_util.file_archiver import archive_files
import traceback


logger = logging.getLogger('edudl2')


def rsync(*args, **kwargs):
    '''
    when cron is used, all exceptions are ignored and no log in the system.
    To solve this issue, we catch exceptions in here and log them.
    '''
    try:
        _rsync(*args, **kwargs)
    except:
        logger.error(traceback.format_exc())
        raise


def _rsync(*args, **kwargs):
    '''
    executing rsync command
    '''
    with tempfile.TemporaryDirectory(prefix='file_grabber') as tmp:
        settings = args[0]
        rsync_command = ['rsync', '-rltzu', '--exclude', '*.partial', '--remove-source-files']
        remote_user = settings.get('file-grabber.args.remote_user')
        remote_host = settings.get('file-grabber.args.remote_host')
        remote_dir = settings.get('file-grabber.args.remote_dir')
        landing = settings.get('file-grabber.args.landing')
        s3_bucket = settings.get('file-grabber.args.archive_s3_bucket_name')
        s3_to_glacier_after_days = int(settings.get('file-grabber.args.archive_s3_to_glacier_after_days', '30'))
        s3_prefix = settings.get('file-grabber.args.archive_s3_prefix')
        private_key = settings.get('file-grabber.args.private_key')
        rsync_ssh = "ssh -o StrictHostKeyChecking=no"
        if private_key is not None:
            rsync_ssh += " -i " + private_key
        rsync_command.append("-e")
        rsync_command.append(rsync_ssh)

        if not remote_dir.endswith('/'):
            remote_dir += '/'
        if not landing.endswith('/'):
            landing += '/'
        rsync_command.append(remote_user + '@' + remote_host + ':' + remote_dir)
        rsync_command.append(tmp)
        returncode = subprocess.call(rsync_command)
        if returncode is not 0:
            logger.error('failed rsync. return code: ' + str(returncode))
        else:
            # copy from temporary directory to actual landing directory
            # using 2 steps copy because of archiving
            for dirpath, dirs, files in os.walk(tmp):
                for filename in files:
                    fname = os.path.abspath(os.path.join(dirpath, filename))
                    dest_path = os.path.join(landing, dirpath[len(tmp) + 1:])
                    os.makedirs(dest_path, exist_ok=True)
                    shutil.copy2(fname, dest_path)
            archive_files(tmp, s3_bucket, s3_to_glacier_after_days, prefix=s3_prefix)
