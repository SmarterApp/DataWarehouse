"""
Methods for adding a user that is able to run the UDL

"""
import os
import subprocess
import pwd


__author__ = 'swimberly'


def create_sftp_user(tenant, user, role, sftp_conf):
    """
    Create an sftp user
    :param tenant: the name of the tenant that the user will belong to
    :param user: the username for the user
    :param role: the role the user will have in the system
    :param sftp_conf: the sftp configuration dictionary
    :return: a tuple containing True if successful, False otherwise and the reason
        as a string
    """
    arrive_depart_dir = sftp_conf['group_directories'][role]
    tenant_path = os.path.join(sftp_conf['sftp_home'], sftp_conf['sftp_base_dir'],
                               arrive_depart_dir, tenant)

    valid_user = verify_user_tenant_and_role(tenant_path, user, role)
    if not valid_user[0]:
        return False, valid_user[1]

    user_path = os.path.join(tenant_path, user)
    create_user(user, user_path, role)
    return True, ""


def create_user(user, home_folder, role):
    """
    create the given user with the specified home-folder and group

    :param user: the username of the user to create
    :param home_folder: the path to the users home folder
    :param role: the name of the user's role which will be used to assign a user to a group
    :return:
    """
    add_user_cmd = "adduser --home {} -g {} {}".format(home_folder, role, user)
    subprocess.call(add_user_cmd, shell=True)


def verify_user_tenant_and_role(tenant_path, username, role, sftp_conf):
    """
    Verify that the username does not already exist and that the tenant does exist

    :param tenant_path: The path to the tenant directory
    :param username: The name of the user being created
    :param role: The role of the user being created (group)
    :return: True if both the tenant and the user are valid, False otherwise
    """
    # Ensure that tenant has already been created
    if not os.path.exists(tenant_path):
        return False, 'Tenant does not exist!'

    # check that the role has been created as a group on the system
    if role not in sftp_conf['groups']:
        return False, 'Role does not exist as a group in the system'

    # Verify that user does not already exist
    try:
        pwd.getpwnam(username)
        return False, 'User already exists!'
    except KeyError:
        return True, ""