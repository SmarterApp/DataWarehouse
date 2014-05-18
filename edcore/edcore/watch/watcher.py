__author__ = 'sravi'

import os
import fnmatch
import time
import ast
import logging
from edcore.watch.util import set_interval, FileUtil
from edcore.watch.file_hasher import MD5Hasher
from edcore.watch.constants import WatcherConstants as Const
from edcore import DEFAULT_LOGGER_NAME

watch_interval = 2


class FileWatcher():
    """File sync class to watch for complete files"""

    def __init__(self, config, append_logs_to=DEFAULT_LOGGER_NAME):
        self.conf = config
        self.file_stats = {}
        self.hasher = MD5Hasher()
        global watch_interval
        watch_interval = self.conf.get(Const.FILE_STAT_WATCH_INTERVAL, 2)
        self.source_path = os.path.join(self.conf.get(Const.BASE_DIR), self.conf.get(Const.SOURCE_DIR))
        self.logger = logging.getLogger(append_logs_to)

    def include_file_missing_checksum(self, source_file):
        """handle files missing checksum file

        Returns true if age of file is too old than a defined threshold else False
        """
        file_last_modified = FileUtil.get_file_last_modified_time(source_file)
        # check if age of file is greater than threshold to wait for checksum file
        if int(file_last_modified and (time.time() - file_last_modified)) > \
                int(self.conf.get(Const.FILE_CHECKSUM_THRESHOLD_WAIT_PERIOD)):
                return True
        return False

    def _verify_source_file_check_sum(self, source_file, checksum_file):
        file_hash = self.hasher.get_file_hash(source_file)
        return FileUtil.file_contains_hash(checksum_file, file_hash)

    def valid_check_sum(self, source_file):
        checksum_file = FileUtil.get_complement_file_name(source_file)
        if not os.path.exists(source_file):
            return False
        if not os.path.exists(checksum_file):
            return self.include_file_missing_checksum(source_file)
        return self._verify_source_file_check_sum(source_file, checksum_file)

    def clear_file_stats(self):
        self.file_stats.clear()

    def get_file_stats(self):
        return self.file_stats

    def find_all_files(self):
        if self.conf is None:
            raise Exception('Invalid Config object')

        self.clear_file_stats()
        for root, dirs, files in os.walk(self.source_path):
            filtered_files = [filename for pattern in set(ast.literal_eval(self.conf.get(Const.FILE_PATTERNS_TO_WATCH)))
                              for filename in fnmatch.filter(files, pattern)]
            # filter hidden file
            filtered_files = [filename for filename in filtered_files if not filename.startswith('.')]
            for filename in filtered_files:
                file_path = os.path.join(root, filename)
                file_stat = FileUtil.get_file_stat(file_path)
                if file_stat is not None:
                    self.file_stats[file_path] = file_stat

    def get_updated_file_stats(self):
        return {filename: FileUtil.get_file_stat(filename) for filename in self.file_stats.keys()}

    @set_interval(interval=watch_interval)
    def watch_and_filter_files_by_stats_changes(self):
        file_stats_latest = self.get_updated_file_stats()
        for file, stat in self.file_stats.copy().items():
            if file_stats_latest[file] is None or file_stats_latest[file] != stat:
                self.logger.debug('Removing file {file} due to size changes during monitoring'.format(file=file))
                self.remove_file_pair_from_dict(file)

    def watch_files(self):
        """Watches the files for the defined duration and discards file undergoing change"""
        # monitor the files for change in stats
        stop = self.watch_and_filter_files_by_stats_changes()
        # monitor for a duration
        time.sleep(float(self.conf.get(Const.FILE_STAT_WATCH_PERIOD)))
        # stop the timer
        stop.set()

    def remove_file_from_dict(self, file):
        self.file_stats.pop(file, None)

    def remove_file_pair_from_dict(self, file):
        # check the file being removed and remove the corresponding pair file
        self.remove_file_from_dict(FileUtil.get_complement_file_name(file))
        # remove the main file
        self.remove_file_from_dict(file)

    def filter_files_for_digest_mismatch(self):
        """Verifies checksum for all the files (ignoring '*.done' files) currently being watched"""
        all_files = self.file_stats.keys()
        # filter out the checksum files which will contain the checksum for a corresponding source file
        source_files = set(all_files) - set(fnmatch.filter(all_files, '*' + Const.CHECKSUM_FILE_EXTENSION))
        for file in source_files:
            if not self.valid_check_sum(file):
                self.logger.error('Removing file {file} due to invalid/missing checksum'.format(file=file))
                self.remove_file_pair_from_dict(file)

    def filter_checksum_files(self):
        """Remove checksum files"""
        for file in set(fnmatch.filter(self.file_stats.copy().keys(), '*' + Const.CHECKSUM_FILE_EXTENSION)):
            self.remove_file_from_dict(file)
