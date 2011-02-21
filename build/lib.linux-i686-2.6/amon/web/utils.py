import json

def string_to_dict(string):
	
	try:
		_convert = string.replace("'", '"')	
	
		return json.loads(_convert)
	except:
		return	False
