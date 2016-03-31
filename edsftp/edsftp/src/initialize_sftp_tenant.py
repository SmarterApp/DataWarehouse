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

__author__ = 'swimberly'

import os
from edsftp.src.util import create_path


def create_tenant(tenant, sftp_conf):
    '''
    Create the necessary directories for the given tenant
    :param tenant: The name of the tenant
    :param sftp_conf: The configuration information for the tenant
    :return: None
    '''
    dir_list = create_list_of_dirs_for_tenant(tenant, sftp_conf)

    print('Directories created for tenant:')
    for path in dir_list:
        create_path(path)
        os.chmod(path, 0o755)
        print('\t', path)


def remove_tenant(tenant, sftp_conf):
    """
    Remove a tenants directories
    :param tenant: The name of the tenant
    :param sftp_conf: sftp configuration information
    :return: None
    """
    dir_list = create_list_of_dirs_for_tenant(tenant, sftp_conf)

    print('Directories removed for tenant:')
    try:
        for path in dir_list:
            os.rmdir(path)
            print('\t', path)
    except OSError:
        print("All users must be removed before tenant can be removed")


def create_list_of_dirs_for_tenant(tenant, sftp_conf):
    """
    Create a list of directory strings that are necessary for the tenant to be created
    :param tenant: The name of the tenant
    :param sftp_conf: The configuration information for the tenant
    :return: None
    """
    return [create_tenant_path_string(tenant, sftp_conf, True),
            create_tenant_path_string(tenant, sftp_conf, False),
            create_tenant_home_folder_string(tenant, sftp_conf, True),
            create_tenant_home_folder_string(tenant, sftp_conf, False)]


def create_tenant_path_string(tenant, sftp_conf, is_arrivals=True):
    """
    Create the path for the tenant
    :param tenant: the tenant name to use for creating the path
    :param sftp_conf: the sftp configuration dictionary
    :param is_arrivals: create the arrivals directory or the departures directory
    :return: a string containing the path to be created
    """
    zone_str = sftp_conf['arrivals_dir'] if is_arrivals else sftp_conf['sftp_departures_dir']
    tenant_path = os.path.join(sftp_conf['home'], sftp_conf['base_dir'], zone_str, tenant)
    return tenant_path


def create_tenant_home_folder_string(tenant, sftp_conf, is_arrivals=True):
    """
    Create the home directory path for the tenant
    This path is almost the same as
    :param tenant: the tenant name to use for creating the path
    :param sftp_conf: the sftp configuration dictionary
    :param is_arrivals: create the arrivals directory or the departures directory
    :return: a string containing the path to be created
    """
    zone_str = sftp_conf['arrivals_dir'] if is_arrivals else sftp_conf['sftp_departures_dir']
    tenant_path = os.path.join(sftp_conf['user_home_base_dir'], zone_str, tenant)
    return tenant_path
