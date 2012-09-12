from keys import key, secret
import os
path = os.path.dirname(os.path.abspath(__file__))

version = "1.0.2"

from boto.s3.key import Key
from boto.s3.connection import S3Connection
conn = S3Connection(key, secret)

uninstall_bucket = conn.get_bucket('uninstall.amon.cx')
install_bucket = conn.get_bucket('install.amon.cx')
contrib_bucket = conn.get_bucket('config.amon.cx')

k = Key(uninstall_bucket)

distros = ['macos']

uninstallers = list(distros)
uninstallers.append('uninstaller')

for u in uninstallers:
    k.key = u
    full_path = "{0}/uninstallers/{1}".format(path, u)
    k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
    k.make_public()

k = Key(install_bucket)

installers = list(distros)
installers.append('installer')

for i in installers:
    k.key = i
    full_path = "{0}/installers/{1}".format(path, i)
    k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
    k.make_public()


# Deploy contrib files
k = Key(contrib_bucket)
for distro in distros:
    if distro != 'macos':
        file = 'mongodb'
        k.key = "{0}/{1}".format(distro, file)
        full_path = "{0}/contrib/mongodb/{1}/{2}".format(path, distro, file)
        k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
        k.make_public()

 # Deploy single files
k.key = 'mongodb.conf'
full_path = "{0}/contrib/mongodb/mongodb.conf".format(path)
k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
k.make_public()


k.key = 'amon'
full_path = "{0}/contrib/amon/amon".format(path)
k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
k.make_public()


k.key = 'amond'
full_path = "{0}/contrib/amon/amond".format(path)
k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
k.make_public()


k.key = 'amon.conf'
full_path = "{0}/config/amon.conf".format(path)
k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
k.make_public()
