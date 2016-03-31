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
Created on Jul 21, 2014

@author: tosako
'''
import os
import fcntl
import logging
from smarter_score_batcher.utils.constants import Constants
import argparse
from smarter_score_batcher.utils.file_lock import FileLock
from smarter_score_batcher.error.exceptions import TSBException, \
    MetadataDirNotExistException
from smarter_score_batcher.error.error_codes import ErrorSource


logger = logging.getLogger("smarter_score_batcher")


def metadata_generator_top_down(dir_path, metadata_filename=Constants.METADATA, recursive=True, force=True):
    '''
    generate metadata from a parent directory to child directories
    :param dir_path: directory to generate metadata
    :param metadata_filename: metadata basename
    :param recursive: generate metadata recursivly
    :param force: generate metadata even if metadata is already existed.
    '''
    if os.path.isdir(dir_path):
        logger.info('seaching directory: [' + dir_path + ']')
        # list directories and files
        directories = [os.path.join(dir_path, d) for d in os.listdir(dir_path)]
        if recursive:
            for directory in directories:
                if os.path.isdir(directory):
                    metadata_generator_top_down(directory, metadata_filename=metadata_filename, recursive=recursive, force=force)
        try:
            with FileMetadata(dir_path, metadata_filename=metadata_filename) as fileMeatadata:
                fileMeatadata.read_files()
                fileMeatadata.write()
                logger.info('generated metadata: [' + fileMeatadata.name + ']')
        except TSBException as e:
            e.err_source = ErrorSource.METADATA_GENERATOR_TOP_DOWN
            e.err_input = 'metadata_filename: ' + metadata_filename
            raise e
    else:
        logger.info('[' + dir_path + '] is not directory')
        raise MetadataDirNotExistException('[' + dir_path + '] is not directory', err_source=ErrorSource.METADATA_GENERATOR_TOP_DOWN, err_input='metadata_filename: ' + metadata_filename)


def metadata_generator_bottom_up(file_path, metadata_filename=Constants.METADATA, recursive=True, generateMetadata=False):
    '''
    generate metadata for one file then update parent directories.
    :param file_path: filename to be updated for metadata
    :param metadata_filename: metadata basename
    :param recursive: update metadata recursivly
    :param generateMetadata: generate an empty metadata file first if it does not eixst
    '''
    dirname = os.path.dirname(file_path)
    updating_metadata = os.path.join(dirname, metadata_filename)
    if not os.path.exists(updating_metadata) and generateMetadata:
        # create empty metadata file
        open(updating_metadata, 'a').close()
    if os.path.isfile(updating_metadata):
        dir_path = os.path.dirname(file_path)
        try:
            with FileMetadata(dir_path, metadata_filename=metadata_filename) as fileMetadata:
                fileMetadata.load_metadata()
                fileMetadata.read_file(file_path)
                fileMetadata.write()
        except TSBException as e:
            e.err_source = ErrorSource.METADATA_GENERATOR_BOTTOM_UP
            e.err_input = 'metadata_filename: ' + metadata_filename
            raise e
        if recursive:
            metadata_generator_bottom_up(dirname, metadata_filename=metadata_filename, recursive=recursive)


class FileMetadata(FileLock):
    '''
    create file metadata to each directories and recursivly.
    /path/.metadata
    file_type:base_file_name:file_size:file_creation_date
    Instantiate FileMetadata with "with" statement in order to take advantage of file lock for metadata.
    '''
    def __init__(self, dir_path, metadata_filename=Constants.METADATA):
        '''
        Constructor
        :param dir_path: directory to generate metadata
        :param metadata_filename: metadata filename
        '''
        self.__path = os.path.abspath(dir_path)
        self.__metadata_filename = metadata_filename
        if os.path.isdir(dir_path):
            self.__metadat_file_path = os.path.join(self.__path, self.__metadata_filename)
        else:
            raise MetadataDirNotExistException('[' + dir_path + '] is not directory')
        self.__dirs = {}
        self.__files = {}
        super().__init__(self.__metadat_file_path)

    def load_metadata(self, delimiter=':'):
        '''
        load metadata into memory
        :param delimiter: metadata field delimiter
        '''
        def setMetadata(metainfo):
            metainfo.name = meta[1]
            metainfo.size = meta[2]
            metainfo.time = meta[3]
            return metainfo
        if os.fstat(self.file_object.fileno()).st_size > 0:
            self.file_object.seek(0)
            for l in self.file_object:
                meta = l.strip().split(delimiter)
                if meta[0] == Constants.DIRECTORY:
                    dirinfo = FileMetadata.DirInfo()
                    metainfo = setMetadata(dirinfo)
                    self.__dirs[metainfo.name] = metainfo
                elif meta[0] == Constants.FILE:
                    fileinfo = FileMetadata.FileInfo()
                    metainfo = setMetadata(fileinfo)
                    self.__files[metainfo.name] = metainfo
            self.file_object.seek(0)

    def read_files(self, force=True):
        '''
        read all files in the directory
        :param force: generate metadata even if it is already exist
        '''
        if not force and os.path.exists(self.__metadat_file_path):
            return False
        # list files and directories
        files = [os.path.join(self.__path, f) for f in os.listdir(self.__path)]
        for file in files:
            self.read_file(file)
        return True

    def read_file(self, file):
        '''
        read a file stat for file size and ctime
        :param file: specific file to updaet metadata
        '''
        basename = os.path.basename(file)
        if os.path.exists(file):
            if os.path.isfile(file):
                if not basename.startswith('.') and basename != self.__metadata_filename:
                    '''
                    do not read hidden file or metadata file
                    '''
                    fileinfo = FileMetadata.FileInfo()
                    fileinfo.read_file_info(file)
                    self.__files[basename] = fileinfo
            elif os.path.isdir(file) and not basename.startswith('.'):
                '''
                do not read hidden directory
                '''
                dirinfo = FileMetadata.DirInfo()
                dirinfo.read_dir_info(file)
                self.__dirs[basename] = dirinfo
        else:
            # possibly file is deleted
            self.__files.pop(basename, None)
            self.__dirs.pop(basename, None)

    @property
    def name(self):
        return self.__metadat_file_path

    @staticmethod
    def _format(file, delimiter=':'):
        '''
        metadata formatter
        '''
        return file.type + delimiter + file.name + delimiter + str(file.size) + delimiter + str(file.time)

    def write(self):
        '''
        metadata file writer
        '''
        def _write(fd, info):
            for d in sorted(info, key=lambda x: x.name):
                '''
                write in alphabetical order
                '''
                if fd.tell() > 0:
                    fd.write('\n')
                fd.write(self._format(d))
        if self.__files or self.__dirs:
            self.file_object.truncate(0)
            _write(self.file_object, list(self.__dirs.values()))
            _write(self.file_object, list(self.__files.values()))

    class DirInfo():
        '''
        metadata for directory
        '''
        def __init__(self):
            pass

        def read_dir_info(self, dir_path, metadata_filename=Constants.METADATA, delimiter=':'):
            '''
            read direcotry stat and all metadatas from children directories
            :param dir_path: directory to update metadata
            :param metadata_filename: metadata filename
            '''
            self.__dir_path = dir_path
            stat_info = os.stat(dir_path)
            self.__last_c_time = stat_info.st_ctime
            self.__metadata_filename = metadata_filename
            self.__size = self.get_size(delimiter=delimiter)

        def read_metadata(self, delimiter=':'):
            '''
            read a metadata file under the child directory
            :param delimiter: metadata field delimiter
            '''
            metadata = []
            metadata_file = os.path.join(self.__dir_path, self.__metadata_filename)
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    fcntl.flock(f, fcntl.LOCK_EX)
                    for line in f:
                        metadata.append(line.strip().split(delimiter))
                    fcntl.flock(f, fcntl.LOCK_UN)
            return metadata

        def get_size(self, delimiter=':'):
            '''
            sum up file/directory size from metadata
            :return: total file/directory size
            '''
            size = 0
            metadata = self.read_metadata(delimiter=delimiter)
            for m in metadata:
                size += int(m[2])
            return size

        @property
        def name(self):
            return os.path.basename(self.__dir_path)

        @name.setter
        def name(self, value):
            self.__dir_path = value

        @property
        def size(self):
            return self.__size

        @size.setter
        def size(self, value):
            self.__size = value

        @property
        def time(self):
            return self.__last_c_time

        @time.setter
        def time(self, value):
            self.__last_c_time = value

        @property
        def type(self):
            return Constants.DIRECTORY

    class FileInfo():
        '''
        metadata for file
        '''
        def __init__(self):
            pass

        def read_file_info(self, filename):
            '''
            read file stat
            :param filename: directory to update metadata
            '''
            self.__filename = filename
            stat_info = os.stat(filename)
            self.__last_c_time = stat_info.st_ctime
            self.__file_size = stat_info.st_size

        @property
        def name(self):
            return os.path.basename(self.__filename)

        @name.setter
        def name(self, value):
            self.__filename = value

        @property
        def size(self):
            return self.__file_size

        @size.setter
        def size(self, value):
            self.__file_size = value

        @property
        def time(self):
            return self.__last_c_time

        @time.setter
        def time(self, value):
            self.__last_c_time = value

        @property
        def type(self):
            return Constants.FILE


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Metadata generator')
    parser.add_argument('-p', '--path', help='directory/file path to read', required=True)
    parser.add_argument('-r', '--recursive', help='generate metadata recursively', action='store_true', default=True)
    parser.add_argument('-m', '--metadata', help='metadata filename', default='.metadata')
    parser.add_argument('-f', '--force', help='force generate metadata if exists', action='store_true', default=False)
    parser.add_argument('-u', '--up', help='update metadat from bottom to up', action='store_true', default=False)
    args = parser.parse_args()
    __path = args.path
    __recursive = args.recursive
    __metadata = args.metadata
    __force = args.force
    __up = args.up

    if __up:
        metadata_generator_bottom_up(__path, metadata_filename=__metadata, recursive=__recursive)
    else:
        metadata_generator_top_down(__path, metadata_filename=__metadata, recursive=__recursive, force=__force)
