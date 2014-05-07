"""
Created on Oct 17, 2013

Module to configure sftp zones
"""

__author__ = 'sravi'

import os
import sys
import shutil
import subprocess
from edsftp.src.util import create_path, change_owner


def _create_sftp_base_dir(sftp_conf):
    """
    create sftp base dir if not exists
    :param None
    :return: None
    """
    if os.path.exists(sftp_conf['home']):
        create_path(os.path.join(sftp_conf['home'], sftp_conf['base_dir']))


def _create_sftp_arrivals_zone(sftp_conf):
    """
    create sftp arrivals zone
    :param None
    :return: None
    """
    if os.path.exists(os.path.join(sftp_conf['home'], sftp_conf['base_dir'])):
        create_path(os.path.join(sftp_conf['home'], sftp_conf['base_dir'], sftp_conf['arrivals_dir']))


def _create_sftp_arrivals_sync_user(sftp_conf):
    """
    create sftp arrivals sync user. This user will be used to run the sftp sync script
    :param sftp_conf
    """
    subprocess.call(['useradd', sftp_conf['arrivals_sync_user']])


def _create_sftp_arrivals_sync_zone(sftp_conf):
    """
    create sftp arrivals sync zone. This is the zone from which remote udl2 machine syncs completely uploaded files
    :param sftp_conf
    :return: None
    """
    arrivals_sync_dir = os.path.join(sftp_conf['home'], sftp_conf['base_dir'], sftp_conf['arrivals_sync_dir'])
    if os.path.exists(os.path.join(sftp_conf['home'], sftp_conf['base_dir'])):
        create_path(arrivals_sync_dir)
    if sys.platform == 'linux':
        _create_sftp_arrivals_sync_user(sftp_conf)
        change_owner(arrivals_sync_dir, sftp_conf['arrivals_sync_user'], sftp_conf['arrivals_sync_user'])
    else:
        print('Not a Unix machine. Not adding sftp sync user: %s' % sftp_conf['arrivals_sync_user'])


def _create_sftp_departures_zone(sftp_conf):
    """
    create sftp departures zone
    :param None
    :return: None
    """
    if os.path.exists(os.path.join(sftp_conf['home'], sftp_conf['base_dir'])):
        create_path(os.path.join(sftp_conf['home'], sftp_conf['base_dir'], sftp_conf['sftp_departures_dir']))


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
    _create_sftp_arrivals_sync_zone(sftp_conf)
    _create_sftp_departures_zone(sftp_conf)
    print('SFTP zone initialized successfully')


def cleanup(sftp_conf):
    sftp_zone_path = os.path.join(sftp_conf['home'], sftp_conf['base_dir'])
    _cleanup_sftp_zone(sftp_zone_path)
    print('SFTP zone cleanedup successfully')
