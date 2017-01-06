from amon.apps.core.basemodel import BaseModel

class BaseDeviceModel(BaseModel):

    def __init__(self):
        super(BaseDeviceModel, self).__init__()
        self.collection = self.mongo.get_collection(self.collection_name)  # Pylint displays errors for undefined self, it actually works fine


    def get_by_name(self, server=None, name=None):
        server_id = server['_id']

        params = {'name': name, 'server_id': server_id}
        result = self.collection.find_one(params)

        return result


    def get_or_create(self, server_id=None, name=None):
        params = {"server_id": server_id, "name": name}
        result = super(BaseDeviceModel, self).get_or_create(params)

        self.collection.ensure_index([('server_id', self.desc)], background=True)

        return result


    def get_data_collection(self, server_id=None):
        data_collection_name = "{0}_data".format(self.device_type)
        collection = self.mongo.get_collection(data_collection_name)

        return collection

    def get_all_for_servers_list(self, servers=None):
        server_ids_list = [self.object_id(x.get('_id')) for x in servers]
        result = self.collection.find({"server_id": {"$in": server_ids_list}})

        return result


    def get_all_for_server(self, server_id=None):
        result = None
        server_id = self.object_id(server_id)

        if server_id:
            result = self.collection.find({"server_id": server_id})

        return result



    def get_check_for_timestamp(self, server, timestamp):
        result_dict = {}
        server_id = server['_id']
        devices = self.get_all_for_server(server_id=server_id)
        data_collection = self.get_data_collection(server_id=server_id)

        if devices:
            for device in devices:
                params = {'device_id':device['_id'], 't': timestamp}
                result_dict[device.get('name')] = data_collection.find_one(params)


        return result_dict


    def save_data(self, server=None, data=None, time=None, expires_at=None):
        server_id = server['_id']
        valid_devices = []

        # New golang agent
        if type(data) == list:
            formated_data = {}
            for d in data:
                name = d.get('name')
                valid_devices.append(name)
                formated_data[name] = d

        # Legacy agent
        else:
            formated_data = data
            try:
                device_list = formated_data.keys()
            except:
                device_list = []

            valid_devices = filter(lambda x: x not in ['time','last','lo'], device_list)

        for device in valid_devices:

            device_object = self.get_or_create(server_id=server_id, name=device)
            device_id = device_object.get('_id')


            try:
                device_data = formated_data[device]
            except:
                device_data = None


            if device_data:

                device_data['t'] = time
                device_data["expires_at"] = expires_at
                device_data['device_id'] = device_id
                device_data['server_id'] = server_id


                if hasattr(self, "compressed_keys"):
                    device_data = self.rename_keys(device_data, self.compressed_keys)

            
                try:
                    del device_data['_id']
                except:
                    pass
                self.update({'last_update': time}, device_id)

                collection = self.get_data_collection(server_id=server_id)
                collection.insert(device_data)

                collection.ensure_index([('t', self.desc)], background=True)
                collection.ensure_index([('device_id', self.desc)], background=True)
                collection.ensure_index([('server_id', self.desc)], background=True)

                collection.ensure_index([('expires_at', 1)], expireAfterSeconds=0)




class InterfacesModel(BaseDeviceModel):

    def __init__(self):
        self.device_type = 'interface'
        self.collection_name = 'interfaces'
        self.compressed_keys = {'inbound': 'i', 'outbound': 'o'}

        super(InterfacesModel, self).__init__()



class VolumesModel(BaseDeviceModel):

    def __init__(self):
        self.device_type = 'volume'
        self.collection_name = 'volumes'

        super(VolumesModel, self).__init__()



volumes_model = VolumesModel()
interfaces_model = InterfacesModel()
