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

'''
Created on Nov 8, 2013

@author: dip
'''


class Config():
    MAX_RETRIES = 'extract.retries_allowed'
    RETRY_DELAY = 'extract.retry_delay'
    TIMEOUT = 'extract.timeout'
    HOMEDIR = 'extract.gpg.homedir'
    BINARYFILE = 'extract.gpg.path'
    KEYSERVER = 'extract.gpg.keyserver'
    TENANT = 'extract.gpg.'
    PICKUP_ROUTE_BASE_DIR = 'extract.sftp.route.base_dir'
    MAIL_SERVER = 'extract.mail.server'
    MAIL_SUBJECT = 'extract.mail.subject'
    MAIL_SENDER = 'extract.mail.sender'
    MAIL_USERNAME = 'extract.mail.smtp_username'
    MAIL_PASSWORD = 'extract.mail.smtp_password'

# list of configurations that are specific to edextract
LIST_OF_CONFIG = [(Config.MAX_RETRIES, int, 1),
                  (Config.RETRY_DELAY, int, 60),
                  (Config.TIMEOUT, int, 20),
                  (Config.HOMEDIR, str, '~/.gpg'),
                  (Config.BINARYFILE, str, 'gpg'),
                  (Config.KEYSERVER, str, None),
                  (Config.PICKUP_ROUTE_BASE_DIR, str, 'route'),
                  (Config.MAIL_SERVER, str, 'None'),
                  (Config.MAIL_SUBJECT, str, 'HPZ Notification'),
                  (Config.MAIL_SENDER, str, 'DoNotReply@SmarterBalanced.org'),
                  (Config.MAIL_USERNAME, str, 'None'),
                  (Config.MAIL_PASSWORD, str, 'None'),
                  ]

# Keeps track of configuration related to edextract that is read off from ini
settings = {}


def setup_settings(config):
    '''
    Reads a dictionary of values, and saves the relevant ones to settings

    :param dict config:  dictionary of configuration for application
    '''
    global settings
    for item in LIST_OF_CONFIG:
        key = item[0]
        to_type = item[1]
        default = item[2]
        settings[key] = to_type(config.get(key, default))


def get_setting(key, default_value=None):
    '''
    Given a key, look up value in settings

    :params string key:  lookup key
    '''
    return settings.get(key, default_value)
