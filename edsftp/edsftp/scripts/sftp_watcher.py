__author__ = 'sravi'

import time
import os
import logging
from edcore.watch.watcher import FileWatcher
from edcore.watch.mover import FileMover
from edcore.watch.constants import WatcherConstants as WatcherConst, MoverConstants as MoverConst
from edsftp.src.constants import Constants as SFTPConst
from edsftp import DEFAULT_LOGGER_NAME

logger = logging.getLogger(DEFAULT_LOGGER_NAME)


def get_watcher_conf(config):
    """massages the conf to make it usable for the FileWatcher core module

    :param config: sftp config
    """
    sftp_conf = config
    sftp_conf.update({WatcherConst.SOURCE_DIR: config.get(SFTPConst.ARRIVALS_DIR)})
    return sftp_conf


def get_mover_conf(config):
    """massages the conf to make it usable for the FileMover core module

    :param config: sftp config
    """
    remote_conf = {}
    prefix = 'remote.'
    remote_conf.update({MoverConst.LANDING_ZONE_HOSTNAME: config.get(prefix + MoverConst.LANDING_ZONE_HOSTNAME),
                        MoverConst.SFTP_USER: config.get(prefix + MoverConst.SFTP_USER),
                        MoverConst.PRIVATE_KEY_FILE: config.get(prefix + MoverConst.PRIVATE_KEY_FILE),
                        MoverConst.ARRIVALS_PATH: config.get(prefix + MoverConst.ARRIVALS_PATH),
                        MoverConst.FILE_MOVE_TYPE: config.get(MoverConst.FILE_MOVE_TYPE),
                        WatcherConst.BASE_DIR: config.get(WatcherConst.BASE_DIR),
                        WatcherConst.SOURCE_DIR: config.get(SFTPConst.ARRIVALS_DIR),
                        WatcherConst.STAGING_DIR: config.get(WatcherConst.STAGING_DIR)})
    return remote_conf


def _watch_and_move_files(file_watcher, file_mover):
    """watch and move files from the sftp arrivals zone to arrivals sync zone"""
    files_moved = 0
    file_watcher.find_all_files()
    file_watcher.watch_files()
    file_watcher.handle_missing_checksum_files()
    files_to_move = list(file_watcher.get_file_stats().keys())
    if len(files_to_move) > 0:
        logger.debug('files to move {files_to_move}'.format(files_to_move=files_to_move))
        files_moved = file_mover.move_files(files_to_move)
    return files_moved


def file_sync(config):
    """file sync main entry point

    This is a forever script

    :param config: config needed for file sync
    """
    remote_conf = get_mover_conf(config)
    file_watcher = FileWatcher(get_watcher_conf(config), append_logs_to=DEFAULT_LOGGER_NAME)
    file_mover = FileMover(remote_conf, append_logs_to=DEFAULT_LOGGER_NAME)
    logger.info('Starting file sync loop')
    while True:
        try:
            logger.debug('Searching for new files in {source_dir}'.format(source_dir=config.get(SFTPConst.ARRIVALS_DIR)))
            files_moved = _watch_and_move_files(file_watcher, file_mover)
            logger.debug('Moved {count} files '.format(count=str(files_moved)))
        except KeyboardInterrupt:
            logger.warn('watcher process terminated by a user')
            os._exit(0)
        except Exception as e:
            logger.error(e)
        finally:
            time.sleep(float(file_watcher.conf.get(WatcherConst.FILE_SYSTEM_SCAN_DELAY)))
    logger.warn('Exiting watcher process')
