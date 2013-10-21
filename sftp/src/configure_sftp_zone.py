"""
Created on Oct 17, 2013

Module to initialize the sftp zones and creating groups
"""

__author__ = 'sravi'

import os
import shutil


def _create_path(path):
    """
    create the path as root if not exists
    :param None
    :return: None
    """
    if not os.path.exists(path):
        os.mkdir(path, 0o755)


def _create_sftp_base_dir(sftp_conf):
    """
    create sftp base dir if not exists
    :param None
    :return: None
    """
    if os.path.exists(sftp_conf['sftp_home']):
        _create_path(os.path.join(sftp_conf['sftp_home'], sftp_conf['sftp_base_dir']))


def _create_sftp_arrivals_zone(sftp_conf):
    """
    create sftp arrivals zone
    :param None
    :return: None
    """
    if os.path.exists(os.path.join(sftp_conf['sftp_home'], sftp_conf['sftp_base_dir'])):
        _create_path(os.path.join(sftp_conf['sftp_home'], sftp_conf['sftp_base_dir'], sftp_conf['sftp_arrivals_dir']))


def _create_sftp_departures_zone(sftp_conf):
    """
    create sftp departures zone
    :param None
    :return: None
    """
    if os.path.exists(os.path.join(sftp_conf['sftp_home'], sftp_conf['sftp_base_dir'])):
        _create_path(os.path.join(sftp_conf['sftp_home'], sftp_conf['sftp_base_dir'], sftp_conf['sftp_departures_dir']))


def _cleanup_sftp_zone(sftp_zone_path):
    """
    cleanup the sftp zone. Recursively removes all directory
    :param None
    :return: None
    """
    if os.path.exists(sftp_zone_path):
        shutil.rmtree(sftp_zone_path, True)


def initialize(sftp_conf):
    _create_sftp_base_dir(sftp_conf)
    _create_sftp_arrivals_zone(sftp_conf)
    _create_sftp_departures_zone(sftp_conf)


def cleanup(sftp_conf):
    sftp_zone_path = os.path.join(sftp_conf['sftp_home'], sftp_conf['sftp_base_dir'])
    _cleanup_sftp_zone(sftp_zone_path)
