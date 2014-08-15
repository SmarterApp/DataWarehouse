__author__ = 'sravi'


class WatcherConstants():
    """
    constants related to watcher module
    """
    FILE_STAT_WATCH_INTERVAL = 'file_stat_watch_interval'
    FILE_STAT_WATCH_PERIOD = 'file_stat_watch_period'
    FILE_SYSTEM_SCAN_DELAY = 'file_system_scan_delay'
    FILE_CHECKSUM_THRESHOLD_WAIT_PERIOD = 'file_checksum_threshold_wait_period'
    BASE_DIR = 'base_dir'
    SOURCE_DIR = 'source_dir'
    DEST_DIR = 'dest_dir'
    FILE_PATTERNS_TO_WATCH = 'file_patterns_to_watch'
    CHECKSUM_FILE_EXTENSION = '.done'
    STAGING_DIR = 'staging_dir'


class MoverConstants():
    """
    constants related to mover module
    """
    LANDING_ZONE_HOSTNAME = 'landing_zone_hostname'
    SFTP_USER = 'sftp_user'
    PRIVATE_KEY_FILE = 'private_key_file'
    ARRIVALS_PATH = 'arrivals_path'
    FILE_TENANT = 'file_tenant'
    FILE_USER = 'file_user'
    FILE_MOEV_TYPE = 'file_move_type'
