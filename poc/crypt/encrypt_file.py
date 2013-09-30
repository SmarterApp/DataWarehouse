import os
import gnupg
import argparse
import time

from pprint import pprint
from gnupg_props import *
 
gpg = gnupg.GPG(gnupghome=GNUPG_HOME)
 

parser = argparse.ArgumentParser()
parser.add_argument("--source", dest="source_file")
parser.add_argument("--dest", dest="dest_file")
parser.add_argument("--sendto", dest="sendto")
args = parser.parse_args()

start=time.time()
with open(args.source_file, 'rb') as f:
    status = gpg.encrypt_file(f,args.sendto, output=args.dest_file)
end=time.time()

print ('ok: ', status.ok)
print ('status: ', status.status)
print ('stderr: ', status.stderr)
print ('source file size (B): ', os.path.getsize(args.source_file))
print ('time taken (ms): ', round((end-start)*1000))
print ('encrypted file size (B): ', os.path.getsize(args.dest_file))