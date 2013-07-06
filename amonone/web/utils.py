try:
    import json
except ImportError:
    import simplejson as json
from datetime import datetime
import calendar
import base64
import random
import string
import hashlib
import os 

def json_string_to_dict(string):

    try:
        _convert = string.replace("'", '"')	

        return json.loads(_convert)
    except:
        return	False


def json_list_to_dict(list):

    converted_list = []

    for _dict in list:
        converted_list.append(json_string_to_dict(_dict))


    return converted_list

def generate_api_key():
    key  = base64.b64encode(hashlib.sha256(str(random.getrandbits(32))).digest(), 
            random.choice(['rA','aZ','gQ','hH','hG','aR','DD'])).rstrip('==')

    return key


def generate_random_string(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))