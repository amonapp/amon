from keys import key, secret
import os
path = os.path.dirname(os.path.abspath(__file__))

from boto.s3.key import Key
from boto.s3.connection import S3Connection
conn = S3Connection(key, secret)

uninstall_bucket = conn.get_bucket('uninstall.amon.cx')
k = Key(uninstall_bucket)

distros = ['debian', 'rpm', 'macos']

uninstallers = list(distros)
uninstallers.append('uninstaller')

for u in uninstallers:
	k.key = u
	full_path = "{0}/uninstallers/{1}".format(path, u)
	k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
	k.make_public()

install_bucket = conn.get_bucket('install.amon.cx')
k = Key(install_bucket)

installers = list(distros)
installers.append('installer')

for i in installers:
	k.key = i
	full_path = "{0}/installers/{1}".format(path, i)
	k.set_contents_from_filename(full_path, headers={'Content-Type': 'text/plain'} )
	k.make_public()

# Deploy new Amon versions

amon_archive = 'amon-0.5.2.tar.gz'
amon_bucket = conn.get_bucket('amon')
k = Key(amon_bucket)
k.key = amon_archive
full_path = "{0}/{1}".format(path, amon_archive)

k.set_contents_from_filename(full_path)
k.make_public()
