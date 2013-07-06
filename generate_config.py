import os.path
import uuid
import base64

# Current directory
ROOT = os.path.abspath(os.path.dirname(__file__))

# Check if AmonOne is already installed 
if os.path.exists('/etc/amonone.conf'):
	config_path = '/etc/amonone.conf'	
else:
	config_path =  os.path.join(ROOT, 'amonone.conf')

try:
    import json
except ImportError:
    import simplejson as json

try:
	config_file = file(config_path).read()
	config = json.loads(config_file)
except:
	config = {}

# Change only the secret key
config['secret_key'] = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)

# Write the config file in the same directory
generated_config_path =  os.path.join(ROOT, 'amonone.conf')

with open(generated_config_path,'w+') as f:
	config_contents = json.dumps(config, indent=4)
	f.write(config_contents)

