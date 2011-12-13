import os.path
import uuid
from hashlib import sha1

ROOT = os.path.abspath(os.path.dirname(__file__))
config_path =  os.path.join(ROOT, 'config', 'amon.conf')
generated_config_path =  os.path.join(ROOT, 'amon.conf')

try:
    import json
except ImportError:
    import simplejson as json

try:
	config_file = file(config_path).read()
	config = json.loads(config_file)
except:
	config = {}

config['secret_key'] = sha1(uuid.uuid4().bytes + uuid.uuid4().bytes).hexdigest()


with open(generated_config_path,'w+') as f:
	config_contents = json.dumps(config, indent=4)
	f.write(config_contents)

