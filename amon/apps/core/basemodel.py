from amon.apps.core.mongodb import MongoBackend
from pymongo import DESCENDING, ASCENDING

class BaseModel(object):

    def __init__(self):
        self.mongo = MongoBackend()
        self.db = self.mongo.get_database()

        self.desc = DESCENDING
        self.asc = ASCENDING

        self.collection = None # Defined in the child models

    def object_id(self, object_id_string):

        try:
            object_id = self.mongo.get_object_id(object_id_string)
        except:
            object_id = False

        return object_id


    def mongoid_to_str(self, data, keys):
        new_dict = {}
        for k, v in data.items():
            value = v
            if k in keys:
                if v is not False:
                    value = str(v)

            new_dict[k] = value

        return new_dict

    def keys_to_mongoid(self, data, keys):
        new_dict = {}
        for k, v in data.items():
            # servers = ['55c0b3eb1d41c88634ee3c4c', '55c0b3eb1d41c88634ee3c50']
            if type(v) == list and k in keys:
                strings_to_objects = [self.mongo.get_object_id(string) for string in v]
            # servers = '55c0b3eb1d41c88634ee3c4c'
            else:
                strings_to_objects = self.object_id(v) if k in keys else v

            new_dict[k] = strings_to_objects

        return new_dict

    # CRUD Methods
    def insert(self, data):
        return self.collection.insert(data)

    def update(self, data, id):
        object_id = self.object_id(id)

        if object_id:
            self.collection.update({"_id": object_id}, {"$set": data}, upsert=True)


    def get_one(self, params=None):
        params = params if params else {}

        result = self.collection.find_one(params)

        if result == None:
            result = {}

        return result


    def get(self, params=None):
        return self.collection.find(params)

    def get_all(self, sort_by=None):

        if sort_by == None:
            sort_by = [('_id', DESCENDING)]

        return self.collection.find().sort(sort_by)


    def get_or_create(self, params):
        result = self.collection.find_one(params)

        if result == None:
            self.collection.insert(params)

        result = self.collection.find_one(params)


        return result

    def get_by_id(self, id):
        object_id = self.object_id(id)

        if object_id:
            return self.collection.find_one({"_id": object_id})

    def delete(self, id):
        object_id = self.object_id(id)

        if object_id:
            self.collection.remove(object_id)

    def delete_all(self):
        self.collection.remove()


    def delete_all_and_insert(self,data):
        self.delete_all()
        self.insert(data)

    def clear_y_axis(self, data=None):
        y_axis_sum = sum([x.get('y', 0) for x in data])
        if y_axis_sum == 0:
            data = []

        return data


    ################################
    #
    #    Utility methods
    #
    ################################


    def rename_keys(self, dictionary, keys):
        # Used for data compression. Takes a dictionary with this format:
        #         {'longname': 1, 'evenlongername': 2}
        # and renames the keys to something simpler:
        #         {"l": 1, 'e': 2}
        new_dictionary = {}
        for k, v in dictionary.items():
            new_key = keys.get(k)
            if new_key:
                new_dictionary[new_key] = v
            else:
                new_dictionary[k] = v

        return new_dictionary


    def remove_keys(self, dictionary, keys):
        for k in keys:
            try:
                del dictionary[k]
            except:
                pass

        return dictionary


    # Used to format ints and strings to float values
    def format_float(self, value):
        try:
            result = round(float(value), 2)
        except:
            result = 0

        return result


    ####################################
