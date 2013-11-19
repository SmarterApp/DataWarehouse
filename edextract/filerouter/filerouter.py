'''
Created on Nov 11, 2013

@author: tosako
'''
import os
import stat
import shutil
import syslog
import sys
import signal
import time
import atexit
import argparse

PID_DIR = '/var/run/filerouter'
PID_FILE = 'filerouter.pid'
PROCESS_SUFFIX = '.process'
LOOP = True


class FileRouterException(Exception):
    pass


class GatekeeprException(FileRouterException):
    def __init__(self, message):
        self.__message = message

    def __repr__(self):
        return repr(self.__message)


def _route_for_error_file(original_file_name, route_dir, error_dir):
    '''
    Route from file in route directory to error directory
    '''
    # replace /route/ to /error/
    error_file = original_file_name.replace('/' + route_dir + '/', '/' + error_dir + '/')

    # if error file already exist, delete it.
    if os.path.isfile(error_file):
        os.unlink(error_file)
    # check error directory first.  If the directory does not exist, then mkdir.
    error_dir = os.path.dirname(error_file)
    if not os.path.isdir(error_dir):
        os.makedirs(error_dir, mode=0o700, exist_ok=True)
    # move file to error directory
    os.rename(original_file_name, error_file)
    syslog.syslog(syslog.LOG_INFO, 'File moved: [{}] to [{}]'.format(original_file_name, error_file))


def _route_file_for_gatekeeper(gatekeeper_jailed_home_base, original_file_name, home_base, gatekeeper_reports_subdir, archive_dir, set_file_owner=True):
    '''
    copy file to gatekeeper account.
    '''
    # find destination file name
    # the functino will throw exception if gatekeeper account has not created or file is already existed in the acconut.
    destination_file_name = _get_destination_filename_for_gatekeeper(gatekeeper_jailed_home_base, gatekeeper_reports_subdir, original_file_name)
    destination_file_dir = os.path.dirname(destination_file_name)
    (_filename, _gatekeeper, _tenant) = _get_info_from_file(original_file_name)
    if not os.path.isdir(destination_file_dir):
        os.makedirs(destination_file_dir, mode=0o700, exist_ok=True)
        if set_file_owner:
            os.chown(destination_file_dir, _gatekeeper, -1)
    # rename file to indicate that file is being copying.
    working_file = original_file_name + PROCESS_SUFFIX
    filedir, filename = os.path.split(destination_file_name)
    # create hidden file name for destination. Make invisible for gatekeeper
    hidden_to_file = os.path.join(filedir, "." + filename)
    # start copying file
    os.rename(original_file_name, working_file)
    shutil.copyfile(working_file, hidden_to_file)

    # archive file
    archive_file_name = _get_archive_filename_for_gatekeeper(home_base, archive_dir, original_file_name)
    full_archive_dir = os.path.dirname(archive_file_name)
    if not os.path.isdir(full_archive_dir):
        os.makedirs(full_archive_dir, mode=0o700, exist_ok=True)
        if set_file_owner:
            os.chown(full_archive_dir, _gatekeeper, -1)
    shutil.copyfile(working_file, archive_file_name)

    # make sure copied hidden file is readable to owner
    os.chmod(hidden_to_file, mode=0o700)
    if set_file_owner:
        os.chown(hidden_to_file, _gatekeeper, -1)
        os.chown(archive_file_name, _gatekeeper, -1)
    # make file visible
    os.rename(hidden_to_file, destination_file_name)

    # remove file
    os.unlink(working_file)
    syslog.syslog(syslog.LOG_INFO, 'File moved: [{}] to [{}]'.format(original_file_name, destination_file_name))


def _get_info_from_file(original_file_name):
    '''
    reading file directory structure and return filename, gatekeeper username, and tenant name
    '''
    path = original_file_name.split(os.path.sep)
    filename = path.pop()
    gatekeeper = path.pop()
    tenant = path.pop()
    return filename, gatekeeper, tenant


def _find_files(base, suffix='.zip'):
    '''
    find "*.zip" file recursively by given base dir.
    '''
    filenames = []
    if base is not None:
        mode = os.stat(base).st_mode
        if stat.S_ISREG(mode):
            if os.path.basename(base).endswith(suffix):
                filenames.append(base)
        elif stat.S_ISDIR(mode):
            dirs = os.listdir(base)
            for file in dirs:
                filenames += _find_files(os.path.join(base, file))
    return filenames


def _get_destination_filename_for_gatekeeper(gatekeeper_jailed_home_base, gatekeeper_reports_subdir, original_file_name):
    '''
    copy file from router account to gatekeeper jailed account
    '''
    (filename, gatekeeper, tenant) = _get_info_from_file(original_file_name)
    # check if jailed account path exist.
    gatekeeper_home_dir = os.path.join(gatekeeper_jailed_home_base, tenant, gatekeeper)
    if os.path.isdir(gatekeeper_home_dir):
        # check the file has existed already.
        destination_filename = os.path.join(gatekeeper_home_dir, gatekeeper_reports_subdir, filename)
        if os.path.isfile(destination_filename):
            # file should not be existed there.
            # failed condition
            raise GatekeeprException('File name[{}] has already existed'.format(destination_filename))
    else:
        # most likely sftp jailed account has not created.
        # failed condition
        raise GatekeeprException('Gatekeeper[{}] has not created for SFTP jailed account'.format(gatekeeper))
    return destination_filename


def _get_archive_filename_for_gatekeeper(home_base, archive_dir, original_file_name):
    '''
    compose archive filename
    '''
    (filename, gatekeeper, tenant) = _get_info_from_file(original_file_name)
    # check if jailed account path exist.
    return os.path.join(home_base, tenant, gatekeeper, archive_dir, filename)


def file_routing(gatekeeper_jailed_home_base, gatekeeper_home_base, filerouter_home_dir, gatekeeper_reports_subdir, route_dir, error_dir, archive_dir, set_file_owner=True):
    '''
    main file routing function
    1. find routable file
    2. copy to sftp jailed account
    3. archive
    4. delete file
    '''
    filerouter_home_dir_route = os.path.join(filerouter_home_dir, route_dir)
    files = _find_files(filerouter_home_dir_route)
    for file in files:
        try:
            _route_file_for_gatekeeper(gatekeeper_jailed_home_base, file, gatekeeper_home_base, gatekeeper_reports_subdir, archive_dir, set_file_owner)
        except Exception as e:
            # failed at copy. revert filename and route file to error.
            syslog.syslog(syslog.LOG_ERR, str(e))
            _route_for_error_file(file, route_dir, error_dir)


def daemonize():
    '''
    damonize process
    '''
    # fork process first
    try:
        pid = os.fork()
    except OSError as e:
        sys.stderr.write('Cannot fork.  Failed to start the program [{}]\n'.format(e.strerror))
        sys.exit(1)
    if pid > 0:
        # bye-bye parent
        sys.exit(0)
    # hello child.

    # change working directory to root directory
    os.chdir('/')
    # creating a unique session id
    # make child process as a process group leader to prevent the child process becomes an orphan in the system
    os.setsid()
    # making sure this process has full access to the files.
    os.umask(0)

    if not os.path.isdir(PID_DIR):
        os.mkdir(PID_DIR)
    pid_file = os.path.join(PID_DIR, PID_FILE)
    if os.path.isfile(pid_file):
        sys.stderr.write("File[{}] is already existed.\n".format(pid_file))
        sys.exit(1)
    # running mutual exclusion and running a single copy
    pid_fo = open(pid_file, 'w')
    pid = str(os.getegid())
    pid_fo.write(pid)
    pid_fo.close()
    atexit.register(delete_pid_file, pid_file)

    # closing standard file descriptors
    sys.stdin.flush()
    sys.stdout.flush()
    sys.stderr.flush()
    null_device = os.open(os.devnull, os.O_RDWR)
    os.dup2(null_device, sys.stdin.fileno())
    os.dup2(null_device, sys.stdout.fileno())
    os.dup2(null_device, sys.stderr.fileno())
    os.close(null_device)
    # handling signal
    signal.signal(signal.SIGHUP, sig_handle)
    signal.signal(signal.SIGTERM, sig_handle)


def sig_handle(signum, frame):
    '''
    signal handler
    '''
    global LOOP
    # received signal.  Terminate the process gracefully
    LOOP = False


def delete_pid_file(pid_file):
    os.unlink(pid_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--gatekeeper_jailed_home_base', default='/sftp/opt/edware/home/departure', help='sftp base dir [/sftp/opt/edware/home/departure]')
    parser.add_argument('-g', '--gatekeeper_home_base', default='/opt/edware/home/departure', help='gatekeeper home base dir. [/opt/edware/home/departure]')
    parser.add_argument('-s', '--gatekeeper_report_subdir', default='reports', help='reports directory which saves requesting reports. [reports]')
    parser.add_argument('-f', '--filerouter_home_dir', default='/opt/edware/home/filerouter', help='filerouter username. [/opt/edware/home/filerouter]')
    parser.add_argument('-i', '--interval', default=5, help='Time interval between file checking calls. [5] seconds')
    parser.add_argument('-r', '--route', default='route', help='route directory. [route]')
    parser.add_argument('-e', '--error', default='error', help='error directory. [error]')
    parser.add_argument('-a', '--archive', default='archive', help='archive directory. [archive]')
    parser.add_argument('-b', '--batch', default=False, action='store_true', help='Batch process [False]')
    args = parser.parse_args()
    route_dir = args.route
    error_dir = args.error
    archive_dir = args.archive
    gatekeeper_jailed_home_base = args.gatekeeper_jailed_home_base
    gatekeeper_home_base = args.gatekeeper_home_base
    gatekeeper_reports_subdir = args.gatekeeper_report_subdir
    filerouter_home_dir = args.filerouter_home_dir
    interval = args.interval
    batch_process = args.batch
    syslog.syslog('Starting filerouter program...')
    if batch_process:
        file_routing(gatekeeper_jailed_home_base, gatekeeper_home_base, filerouter_home_dir, gatekeeper_reports_subdir, route_dir, error_dir, archive_dir)
    else:
        daemonize()
        while LOOP:
            file_routing(gatekeeper_jailed_home_base, gatekeeper_home_base, filerouter_home_dir, gatekeeper_reports_subdir, route_dir, error_dir, archive_dir)
            time.sleep(interval)
    syslog.syslog('Exiting filerouter program...')
    sys.exit(0)

if __name__ == "__main__":
    main()
