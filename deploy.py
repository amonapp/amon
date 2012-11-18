from keys import key, secret
import os
path = os.path.dirname(os.path.abspath(__file__))

from boto.s3.key import Key
from boto.s3.connection import S3Connection
conn = S3Connection(key, secret)

uninstall_bucket = conn.get_bucket('uninstall.amon.cx')
install_bucket = conn.get_bucket('install.amon.cx')
contrib_bucket = conn.get_bucket('config.amon.cx')

k = Key(uninstall_bucket)
k.key = 'uninstaller'
full_path = "{0}/uninstaller".format(path)
k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
k.make_public()


k = Key(install_bucket)
k.key = 'installer'
full_path = "{0}/installer".format(path)
k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
k.make_public()

# Deploy contrib files
k = Key(contrib_bucket)

k.key = 'amonlite'
full_path = "{0}/contrib/amonlite".format(path)
k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
k.make_public()


k.key = 'amond'
full_path = "{0}/contrib/amond".format(path)
k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
k.make_public()


k.key = 'amonlite.conf'
full_path = "{0}/config/amonlite.conf".format(path)
k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
k.make_public()
