import json

def flat_to_tree_dict_helper(dictionary, split_symbol='.'):
    """
     Gets a flat dictionary in the following format:

         {"name.first_name": 'Martin', "name.last_name": "Rusev"}

     and converts it to:

         {"name": {"first_name": "Martin", "last_name": "Rusev" }}

     It converts deeper dictionary keys to underscore:

         {"name.first.name": 'Martin', "name.last.name": "Rusev"}

     becomes:


    """
    filtered_dict = {}
    for key, value in dictionary.items():
        key_parts = key.split(split_symbol)

        total_elements = len(key_parts)

        if total_elements > 0:
            first_element = key_parts[0]
            subdocument_key = None

            if len(key_parts[1:]) > 0:
                subdocument_key = "_".join(key_parts[1:])  # Strip dots

            key_exists = filtered_dict.get(first_element)

            if key_exists == None:
                filtered_dict[first_element] = {}


            if type(value) not in [int, float]:
                value = value.replace(',','.')

                try:
                    value = float(value)
                except ValueError:
                    try:
                        value = int(value)
                    except:
                        value = value

            if subdocument_key == None:
                filtered_dict[first_element] = value
            else:
                
                try:
                    filtered_dict[first_element][subdocument_key] = value
                except:
                    pass

    return filtered_dict



def remove_dots(obj):
    for key in obj.keys():
        new_key = key.replace("_",".")
        if new_key != key:
            obj[new_key] = obj[key]
            del obj[key]
    return obj


def replace_underscore_with_dot_helper(dictionary):
    new_dict = json.loads(json.dumps(dictionary), object_hook=remove_dots)

    return new_dict
