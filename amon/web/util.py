import json

def string_to_dict(string):
	_convert = string.replace("'", '"')	
	
	return json.loads(_convert)
