__author__ = 'swimberly'

import time
import os
import shutil

from udl2.celery import udl2_conf

ARRIVED = 'arrived'
DECRYPTED = 'decrypted'
EXPANDED = 'expanded'
SUBFILES = 'subfiles'
HISTORY = 'history'


def move_file_from_arrivals(incoming_file, batch_guid):
    """
    Create the subdirectories for the current batch and mv the incoming file to the proper locations.
    :param incoming_file: the path the incoming file
    :param batch_guid: the guid for the current batch
    :return: A dictionary containing all the created directories
    """
    tenant_name = _get_tenant_name(incoming_file)
    tenant_directory_paths = _create_directory_paths(tenant_name, batch_guid)
    _create_batch_directories(tenant_directory_paths)
    _move_file_to_work_and_history(incoming_file, tenant_directory_paths[ARRIVED], tenant_directory_paths[HISTORY])
    return tenant_directory_paths


def _move_file_to_work_and_history(incoming_file, arrived_dir, history_dir):
    """
    Move the incoming file to its arrived directory under the work folder
        and move it to its history directory
    :param incoming_file: the path to the incoming file
    :param arrived_dir: the directory path to the arrived directory
    :param history_dir: the directory path to the history directory
    :return: None
    """
    shutil.copy2(incoming_file, arrived_dir)
    shutil.move(incoming_file, history_dir)


def _get_tenant_name(incoming_file):
    """
    Given the incoming files path return the name of the tenant
    :param incoming_file: the path to the incoming file
    :return: A string containing the tenant name
    """
    return os.path.split(os.path.dirname(incoming_file))[-1]


def _create_directory_paths(tenant_name, batch_guid):
    """
    Create the path strings to all directories that need to be created for the batch
    :param tenant_name: The name of the tenant
    :param batch_guid: the batch guid for the current run
    :return: a dictionary containing the paths to all directories that need to be created
    """
    dir_name = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    dir_name += '_' + batch_guid

    directories = {
        ARRIVED: os.path.join(udl2_conf['zones']['work'], tenant_name, ARRIVED, dir_name),
        DECRYPTED: os.path.join(udl2_conf['zones']['work'], tenant_name, DECRYPTED, dir_name),
        EXPANDED: os.path.join(udl2_conf['zones']['work'], tenant_name, EXPANDED, dir_name),
        SUBFILES: os.path.join(udl2_conf['zones']['work'], tenant_name, SUBFILES, dir_name),
        HISTORY: os.path.join(udl2_conf['zones']['history'], tenant_name, dir_name)
    }
    return directories


def _create_batch_directories(directory_dict):
    """
    Create all the directories in the given dict
    :param directory_dict: a dictionary of directories
    :return:
    """

    for directory in directory_dict.values():
        os.makedirs(directory, mode=0o777)
