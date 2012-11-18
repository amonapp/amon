from __future__ import with_statement
import os.path
import random
import string

# Current directory
ROOT = os.path.abspath(os.path.dirname(__file__))

# Check if Amon Lite is already installed 
if os.path.exists('/etc/amonlite.conf'):
    config_path = '/etc/amonlite.conf'  
else:
    config_path =  os.path.join(ROOT, 'config', 'amonlite.conf')

try:
    import json
except ImportError:
    import simplejson as json

try:
    config_file = file(config_path).read()
    config = json.loads(config_file)
except:
    config = {}

# Replace with a new secret key
if len(config['secret_key']) != 32:
    config['secret_key'] = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(32))

# Write the config file in the same directory
generated_config_path =  os.path.join(ROOT, 'amonlite.conf')

with open(generated_config_path,'w+') as f:
    config_contents = json.dumps(config, indent=4)
    f.write(config_contents)

