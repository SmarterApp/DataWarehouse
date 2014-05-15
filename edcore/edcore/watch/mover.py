__author__ = 'sravi'

import os
import logging
from edcore.watch.util import SendFileUtil
from edcore.watch.util import FileUtil
from edcore.watch.constants import MoverConstants as MoverConst, WatcherConstants as WatcherConst
from edcore import DEFAULT_LOGGER_NAME


class FileMover():
    """File mover class to move files to needed destination"""
    conf = None
    logger = None

    def __init__(self, config, append_logs_to=DEFAULT_LOGGER_NAME):
        FileMover.conf = config
        FileMover.logger = logging.getLogger(append_logs_to)

    @classmethod
    def move_files(cls, files_to_move):
        files_moved = 0
        for file in files_to_move:
            cls.logger.debug('SFTPing file: ' + file)
            file_tenant_name, file_tenant_user_name = \
                FileUtil.get_file_tenant_and_user_name(file, os.path.join(cls.conf[WatcherConst.BASE_DIR],
                                                                          cls.conf[WatcherConst.SOURCE_DIR]))
            file_transfer_status, proc = \
                SendFileUtil.remote_transfer_file(source_file=file,
                                                  hostname=cls.conf[MoverConst.LANDING_ZONE_HOSTNAME],
                                                  remote_base_dir=cls.conf[MoverConst.ARRIVALS_PATH],
                                                  file_tenantname=file_tenant_name,
                                                  file_username=file_tenant_user_name,
                                                  sftp_username=cls.conf[MoverConst.SFTP_USER],
                                                  private_key_file=cls.conf[MoverConst.PRIVATE_KEY_FILE])
            if file_transfer_status != 0:
                cls.logger.error('File transfer failed for {file} '
                                 'with error {error}'.format(file=file, error=proc.stderr.read().decode()))
            else:
                cls.logger.debug('File transfer was success for {file}'.format(file=file))
                os.remove(file)
                files_moved += 1
                cls.logger.debug('Deleted source file {file}'.format(file=file))

        return files_moved
