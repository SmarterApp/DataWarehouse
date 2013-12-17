'''
Created on Dec 2, 2013

@author: tosako
'''
import os
import io
import zipfile
import gnupg
import tempfile


def import_recipient_keys(gpg, recipients, keyserver):
    keys = gpg.search_keys(recipients, keyserver)
    key_ids = [key['keyid'] for key in keys]
    gpg.recv_keys(keyserver, *key_ids)


def remove_temp_keyring(gpghomedir):
    filelist = [f for f in os.listdir(gpghomedir)]
    for f in filelist:
        os.remove(gpghomedir + os.sep + f)
    os.rmdir(gpghomedir)


def encrypted_archive_files(dirname, recipients, outputfile, homedir=None, keyserver=None, gpgbinary='gpg'):
    '''
    create encrpyted archive file.
    '''
    data = archive_files(dirname).getvalue()
    gpghomedir = None
    if keyserver is None:
        gpg = gnupg.GPG(gnupghome=os.path.abspath(homedir), gpgbinary=gpgbinary)
    else:
        gpghomedir = tempfile.mkdtemp(dir='/tmp')
        gpg = gnupg.GPG(gnupghome=os.path.abspath(gpghomedir), gpgbinary=gpgbinary)
        import_recipient_keys(gpg, recipients, keyserver)
    gpg.encrypt(data, recipients, output=outputfile, always_trust=True)
    if gpghomedir is not None:
        remove_temp_keyring(gpghomedir)


def archive_files(dirname):
    '''
    create archive file under given directory and return zip data
    '''
    bufferedIO = io.BytesIO()
    with zipfile.ZipFile(bufferedIO, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        files = [os.path.join(dirname, f) for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f))]
        for file in files:
            zf.write(file, arcname=os.path.basename(file))
    return bufferedIO
