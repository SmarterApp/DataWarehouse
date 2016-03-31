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

import os
import logging
import gnupg

__author__ = 'sravi'

logger = logging.getLogger(__name__)


def _is_file_exists(file_to_decrypt):
    """
    check if file exists and readable
    :param file_to_decrypt: the path of the file to be decrypted
    :return: boolean true, if the file exists and is readable
    """
    return os.path.isfile(file_to_decrypt) and os.access(file_to_decrypt, os.R_OK)


def _is_valid__file(file_to_decrypt):
    """
    Basic file validation checks before decrypting
    :param file_to_decrypt: the path of the file to be decrypted
    :return: boolean true, if the file is a valid file
    """
    valid = False
    if _is_file_exists(file_to_decrypt):
        valid = True
        logger.info('File exists and is readable -- %s ' % file_to_decrypt)
    else:
        logger.error('File missing or un-readable -- %s ' % file_to_decrypt)

    return valid


def _print_status(status):
    """
    Print the entire gnupg status object after decryption
    :param status: gnupg return status after attempting decryption
    :return: None
    """
    logger.info('ok: %s ' % status.ok)
    logger.debug('status: %s ' % status.status)
    logger.debug('stderr: %s ' % status.stderr)
    if status.ok:
        logger.debug('signer: %s ' % status.username)
        logger.debug('signer key id: %s ' % status.key_id)
        logger.debug('signer key fingerprint: %s ' % status.fingerprint)
        logger.debug('signer signature id: %s ' % status.signature_id)
        logger.debug('signer trust level: %s ' % status.trust_level)
        logger.debug('signer trust text: %s ' % status.trust_text)


def _decrypt_file_contents(file_to_decrypt, output_file, passphrase, gpg_home):
    """
    verify signature, decrypt and write the decrypted file to the destination directory
    :param file_to_decrypt: the path of the file to be decrypted
    :param output_file: the path to write the output decrypted file
    :param passphrase: passphrase to access the secret key for decryption from key repo
    :param gpg_home: Home folder for gpg to fetch the keys
    :return: status: the gnupg status object after attempting decryption
    """
    gpg = gnupg.GPG(gnupghome=gpg_home)
    with open(file_to_decrypt, 'rb') as f:
        status = gpg.decrypt_file(f, passphrase=passphrase, output=output_file)
    return status


def decrypt_file(file_to_decrypt, destination_dir, passphrase, gpg_home):
    """
    Verify and Decrypt the file after needed validations
    :param file_to_decrypt: the path of the file to be decrypted
    :param destination_dir: destination directory path
    :param passphrase: passphrase to access the secret key for decryption from key repo
    :param gpg_home: Home folder for gpg to fetch the keys
    :return status: gpg decryption status object
    :return output_file: full path to the decrypted file
    """
    if not _is_valid__file(file_to_decrypt):
        raise Exception('Invalid source file -- %s' % file_to_decrypt)

    output_file = os.path.join(destination_dir, os.path.splitext(os.path.basename(file_to_decrypt))[0])
    status = _decrypt_file_contents(file_to_decrypt, output_file, passphrase, gpg_home)

    _print_status(status)

    if not status.ok:
        raise Exception('Decryption Failed')
    # TODO: commented out for now, need to fix trust level
    # if status.trust_level is None or status.trust_level < 4:
    #     raise Exception('Verification Failed. Signature not trusted')
    return status, output_file
