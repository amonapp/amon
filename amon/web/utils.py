try:
    import json
except ImportError:
    import simplejson as json

def json_string_to_dict(string):
    
    try:
        _convert = string.replace("'", '"') 
    
        return json.loads(_convert)
    except:
        return  False


def json_list_to_dict(list):
    
    converted_list = []

    for _dict in list:
        converted_list.append(json_string_to_dict(_dict))

    
    return converted_list


