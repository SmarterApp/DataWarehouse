import os
import subprocess
import csv
import math
import argparse
import datetime
import logging
import tarfile

logger = logging.getLogger(__name__)


def _is_file_exists(file_to_expand):
    '''
    check if file exists and readable
    '''
    return os.path.isfile(file_to_expand) and os.access(file_to_expand, os.R_OK)


def _is_tar_file(file_to_expand):
    '''
    check for valid tar file
    '''
    return tarfile.is_tarfile(file_to_expand)


def _is_valid__tar_file(file_to_expand):
    '''
    Basic file validation checks before expanding
    '''
    valid = False
    if _is_file_exists(file_to_expand):
        valid = True
        logger.info("File exists and is readable -- %s " % file_to_expand)
    else:
        logger.error("File missing or un-readable -- %s " % file_to_expand)

    if valid:
        if _is_tar_file(file_to_expand):
            logger.info("Tar file format recongnized -- %s " % file_to_expand)
        else:
            valid = False
            logger.error("Tar file format un-recongnized -- %s " % file_to_expand)
    return valid


def _extract_tar_file_contents(file_to_expand, expanded_dir):
    '''
    extract file contents to the destination directory
    '''
    tar_file_contents = []
    tar = tarfile.open(file_to_expand, "r:gz")
    for tarinfo in tar:
        tar_file_contents.append(expanded_dir + tarinfo.name)
        print(tarinfo.name, tarinfo.size, " bytes in size, is a regular file: ", tarinfo.isreg())
    # TODO: how to deal with file's which are archived with absolute paths
    tar.extractall(expanded_dir)
    tar.close()
    return tar_file_contents


def expand_file(file_to_expand, expanded_dir):
    '''
    Expand the file after needed validations
    '''
    if not _is_valid__tar_file(file_to_expand):
        raise Exception('Invalid source file -- %s' % file_to_expand)

    # the contents of the tar file will be validated as part of simple file validator
    tar_file_contents = _extract_tar_file_contents(file_to_expand, expanded_dir)

    return tar_file_contents


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process file expander args')
    parser.add_argument('-i', '--input', dest="file_to_expand", help='file_to_expand')
    parser.add_argument('-o', '--output', dest="expanded_dir", default='.', help='output directory')

    args = parser.parse_args()
    print("Input file is: " + args.file_to_expand)
    if args.expanded_dir:
        print("Expand files to: " + args.expanded_dir)

    expand_file(args.file_to_expand, args.expanded_dir)
