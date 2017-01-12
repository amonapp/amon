import uuid
import hmac
from hashlib import sha1

from amon.utils import AmonStruct
from amon.utils.dates import unix_utc_now
import json
from bson.json_util import dumps as bson_dumps


def throttle_status(server=None):
    result = AmonStruct()
    result.allow = False

    last_check = server.get('last_check')
    server_check_period = server.get('check_every', 60)

    if last_check:
        period_since_last_check = unix_utc_now() - last_check

        # Add 15 seconds buffer, for statsd
        period_since_last_check = period_since_last_check + 15

        if period_since_last_check >= server_check_period:
            result.allow = True
    else:
        result.allow = True  # Never checked
    
    return result


# Data Format
# {u'dstypes': [u'gauge'],
# u'plugin': u'users', u'dsnames': [u'value'],
#  u'interval': 10.0, u'host': u'ubuntu', u'values': [7], 
#  u'time': 1424233591.485, u'plugin_instance': u'', 
#  u'type_instance': u'', u'type': u'users'}
def parse_statsd_data(data=None):
    plugin_data = {}
    ignored_plugins = ['irq']
    accepted_types = ['gauge', ]

    if len(data) > 0:
        for p in data:
            plugin_name = p.get('plugin')
            plugin_instance = p.get('plugin_instance')
            dsnames = p.get('dsnames')
            values = p.get('values')
            dstypes = p.get('dstypes')

            name = "collectd.{0}".format(plugin_name)

            
            accepted_type = all(t in accepted_types for t in dstypes)
                
            if accepted_type:
                plugin_data[name] = {}
                for dsn, v, dstype in zip(dsnames, values, dstypes):
                    if plugin_name not in ignored_plugins:
                        value_name = "{0}.{1}".format(plugin_instance, dsn) if plugin_instance else dsn
                        value_name = "{0}.{1}".format(plugin_name, value_name) if dsn == 'value' else value_name

                        plugin_data[name][value_name] = v

    return plugin_data


def generate_api_key():
    # From tastipie https://github.com/django-tastypie/django-tastypie/blob/master/tastypie/models.py#L49
    new_uuid = uuid.uuid4()
    key = hmac.new(new_uuid.bytes, digestmod=sha1).hexdigest()

    return key


def dict_from_cursor(data=None, keys=None):
    filtered_dict = {}
    # Convert Uids to str
    data = bson_dumps(data)
    python_dict = json.loads(data)

    for key in keys:
        value = python_dict.get(key)
        if type(value) is dict:
            # Try to get mongo_id
            mongo_id = value.get('$oid')
            if mongo_id:
                value = mongo_id
        
        if key == '_id':
            key = 'id'

        filtered_dict[key] = value


    return filtered_dict
