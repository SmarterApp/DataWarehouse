import os
import argparse
import logging
import tarfile

__author__ = 'sravi'

logger = logging.getLogger(__name__)


def _is_file_exists(file_to_expand):
    """
    check if file exists and readable
    :param file_to_expand: the path to the file to be expanded
    :return: boolean true, if the file exists and is readable
    """
    return os.path.isfile(file_to_expand) and os.access(file_to_expand, os.R_OK)


def _is_tar_file(file_to_expand):
    """
    check for valid tar file
    :param file_to_expand: the path to the file to be expanded
    :return: boolean true, if the file is a valid tar file
    """
    return tarfile.is_tarfile(file_to_expand)


def _is_valid__tar_file(file_to_expand):
    """
    Basic file validation checks before expanding
    :param file_to_expand: the path to the file to be expanded
    :return: boolean true, if the file is a valid tar file and readable
    """
    valid = False
    if _is_file_exists(file_to_expand):
        valid = True
        logger.info("File exists and is readable -- %s " % file_to_expand)
    else:
        logger.error("File missing or un-readable -- %s " % file_to_expand)

    if valid:
        if _is_tar_file(file_to_expand):
            logger.info("Tar file format recognized -- %s " % file_to_expand)
        else:
            valid = False
            logger.error("Tar file format un-recognized -- %s " % file_to_expand)
    return valid


def _verify_tar_file_contents(tar_file):
    """
    Verifies the tar file contents for presence of exactly two files [one csv and one JSON file]
    :param tar_file: list of contents returned by tar module
    :return: raises exception if verification fails
    """
    file_extensions = set([os.path.splitext(file)[1][1:].strip().lower() for file in tar_file.getnames()])
    if len(file_extensions) != 2 or 'csv' not in file_extensions or 'json' not in file_extensions:
        raise Exception('Expected 2 files not found in the tar archive')


def _extract_tar_file_contents(file_to_expand, expanded_dir):
    """
    extract file contents to the destination directory
    :param file_to_expand: the path to the file to be expanded
    :param expanded_dir: the destination directory
    :return: tar_file_contents: the tar file contents as list [path to csv and json files]
    """
    tar_file_contents = []
    tar = tarfile.open(file_to_expand, "r:gz")
    _verify_tar_file_contents(tar)
    for tarinfo in tar:
        tar_file_contents.append(expanded_dir + tarinfo.name)
        print(tarinfo.name, tarinfo.size, " bytes in size, is a regular file: ", tarinfo.isreg())
    # TODO: how to deal with file's which are archived with absolute paths
    tar.extractall(expanded_dir)
    tar.close()
    return tar_file_contents


def expand_file(file_to_expand, expanded_dir):
    """
    Expand the file after needed validations
    :param file_to_expand: the path to the file to be expanded
    :param expanded_dir: the destination directory
    :return: tar_file_contents: the tar file contents as list [path to csv and json files]
    """
    if not _is_valid__tar_file(file_to_expand):
        raise Exception('Invalid source file -- %s' % file_to_expand)

    # the contents of the tar file will be validated as part of simple file validator
    tar_file_contents = _extract_tar_file_contents(file_to_expand, expanded_dir)

    return tar_file_contents


if __name__ == "__main__":
    """
    Entry point to file_expander to run as stand alone script
    """
    parser = argparse.ArgumentParser(description='Process file expander args')
    parser.add_argument('-i', '--input', dest="file_to_expand", help='file_to_expand')
    parser.add_argument('-o', '--output', dest="expanded_dir", default='.', help='output directory')

    args = parser.parse_args()
    print("Input file is: " + args.file_to_expand)
    if args.expanded_dir:
        print("Expand files to: " + args.expanded_dir)

    expand_file(args.file_to_expand, args.expanded_dir)
