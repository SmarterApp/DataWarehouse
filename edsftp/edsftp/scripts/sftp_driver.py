"""
Created on Oct 17, 2013

Module to initialize sftp zones and creating groups
"""

__author__ = 'sravi'

import argparse
import logging
import logging.config
from edsftp.src.configure_sftp_zone import initialize as sftp_zone_init, cleanup as sftp_zone_cleanup
from edsftp.src.configure_sftp_groups import initialize as sftp_groups_init, cleanup as sftp_groups_cleanup
from edsftp.src.initialize_sftp_tenant import create_tenant, remove_tenant
from edsftp.src.initialize_sftp_user import create_sftp_user, delete_user
from edsftp.scripts.sftp_watcher import file_sync
from edcore.utils.utils import read_ini, get_config_from_ini
from edcore.utils.utils import create_daemon
from edcore import DEFAULT_LOGGER_NAME

logger = logging.getLogger(DEFAULT_LOGGER_NAME)


def run_sftp_sync_process(daemon_mode, sftp_conf, pid_file):
    if daemon_mode:
        create_daemon(pid_file)
    file_sync(sftp_conf)


def main():
    """
    Driver script to build and maintain sftp machine
    This script needs to be run as root user
    """
    parser = argparse.ArgumentParser(description='Process sftp driver args')
    parser.add_argument('--init', dest='driver_init_action', action='store_true')
    parser.add_argument('--cleanup', dest='driver_cleanup_action', action='store_true')
    parser.add_argument('--sync', dest='driver_run_sync', action='store_true')
    parser.add_argument('-a', '--add-user', action='store_true', help='create the given username')
    parser.add_argument('-s', '--add-tenant', action='store_true', help='create the given tenant name')
    parser.add_argument('-u', '--username', help='The username to add')
    parser.add_argument('-t', '--tenant-name', help='The tenant name to use')
    parser.add_argument('-r', '--role-name', help='The role that the user should have')
    parser.add_argument('--ssh-key', help='The ssh key for the new user')
    parser.add_argument('--ssh-key-file', help='The path to the file where the ssh key is located. '
                                               'Will not be used if -ssh-key is specified')
    parser.add_argument('--remove-user', action='store_true', help='Delete the user defined by the -u option')
    parser.add_argument('--remove-tenant', action='store_true', help='Remove the tenant specified by the -t option')
    parser.add_argument('-p', dest='pidfile', default='/opt/edware/run/edsftp-watcher.pid',
                        help="pid file for sftp watcher daemon")
    parser.add_argument('-d', dest='daemon', action='store_true', default=False, help="daemon mode for sync option")
    parser.add_argument('-i', dest='ini_file', default='/opt/edware/conf/smarter.ini', help="ini file")
    args = parser.parse_args()

    file = args.ini_file
    logging.config.fileConfig(file)
    settings = read_ini(file)
    sftp_conf = get_config_from_ini(config=settings, config_prefix='sftp', delete_prefix=True)

    if args.driver_init_action:
        sftp_zone_init(sftp_conf)
        sftp_groups_init(sftp_conf)
    elif args.driver_cleanup_action:
        sftp_groups_cleanup(sftp_conf)
        sftp_zone_cleanup(sftp_conf)
    elif args.driver_run_sync:
        daemon_mode = args.daemon
        pid_file = args.pidfile
        run_sftp_sync_process(daemon_mode, sftp_conf, pid_file)
    elif args.add_tenant:
        if args.tenant_name is None:
            parser.error('Tenant name is required to add a new tenant')
        create_tenant(args.tenant_name, sftp_conf)
    elif args.add_user:
        if args.username is None or args.tenant_name is None or args.role_name is None:
            parser.error('Username (-u), tenant name (-t) and role name (-r) are required to add a new user (-a)')
        create_sftp_user(args.tenant_name, args.username, args.role_name, sftp_conf, args.ssh_key)
    elif args.remove_user:
        if args.username is None:
            parser.error('Must specify a username (-u) to delete a user')
        delete_user(args.username)
    elif args.remove_tenant:
        if args.tenant_name is None:
            parser.error("Must specify a tenant name (-t) to delete a tenant")
        remove_tenant(args.tenant_name, sftp_conf)
    else:
        parser.error('Please specify a valid argument')

if __name__ == "__main__":
    main()
