import json
from datetime import datetime
from time import mktime

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


############################# 
#                           #
#   DATE UTILS              #
#                           #
#############################
# Converts date strings: '31-07-2011-17:46' to datetime objects 
def datestring_to_datetime(datestring, format="%d-%m-%Y-%H:%M"):
	return datetime.strptime(datestring, format) 

	
# Converts datetime objects to unix integers
def datetime_to_unixtime(datetime):
	return int(mktime(datetime.timetuple()))

# Converts date string to unix time
def datestring_to_unixtime(datestring):
	datetime_object = datestring_to_datetime(datestring)
	return datetime_to_unixtime(datetime_object)
