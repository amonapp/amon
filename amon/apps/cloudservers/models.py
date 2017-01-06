from amon.apps.core.basemodel import BaseModel
from amon.utils.security import AESCipher
from amon.utils.dates import unix_utc_now


class CloudCredentialsModel(BaseModel):


    def __init__(self):
        super(CloudCredentialsModel, self).__init__()
        self.collection = self.mongo.get_collection('integrations')
        self.metadata_collection = self.mongo.get_collection('integrations_metadata')
        self.encrypted_fields = {
            'digitalocean': ['api_key', 'client_id', 'token'],
            'google': ['email', 'project_id'],
            'amazon': ['access_key', 'secret_key'],
            'linode': ['api_key', 'client_id'],
            'rackspace': ['username', 'api_key'],
            'vultr': ['api_key'],
        }

        self.cypher = AESCipher()

    def _encrypt_fields(self, data, provider_id=None):
        encrypted_fields = self.encrypted_fields.get(provider_id)
        if encrypted_fields:

            for key, value in data.items():
                if key in encrypted_fields:
                    data[key] = self.cypher.encrypt(value)
                else:
                    data[key] = value  # Return everything else 
        return data

    def _decrypt_fields(self, data, provider_id=None):
        encrypted_fields = self.encrypted_fields.get(provider_id)

        if encrypted_fields:

            for key, value in data.items():
                if key in encrypted_fields:
                    data[key] = self.cypher.decrypt(value)
                else:
                    data[key] = value # Return everything else, used in get_by_id

        return data

    def get_by_id(self, id):
        result = None
        query = super(CloudCredentialsModel, self).get_by_id(id)
        if query != None:
            provider_id = query.get('service')
            result = self._decrypt_fields(query, provider_id=provider_id)

        return result


    def get_metadata(self, _type):
        return self.metadata_collection.find({'type': _type})

    def save_metadata(self, params, data):
        self.metadata_collection.update(params, data, upsert=True)
        self.collection.ensure_index([('type', self.desc)], background=True)


    def update_last_sync(self, credentials_id=None):
        data = {'last_sync': unix_utc_now()}
        credentials_id = self.object_id(credentials_id)
        
        self.collection.update({"_id": credentials_id}, {"$set": data}, upsert=True)

    def update(self, data=None, id=None, provider_id=None):
        data = self._encrypt_fields(data, provider_id=provider_id)
        super(CloudCredentialsModel, self).update(data, id)

    def save(self, data=None, provider_id=None):
        data = self._encrypt_fields(data, provider_id=provider_id)
        data['service'] = provider_id
        credentials_id = self.collection.insert(data)

        self.collection.ensure_index([('account_id', self.desc)], background=True)
        self.collection.ensure_index([('service', self.desc)], background=True)

        return credentials_id


    def unset_error(self, credentials_id=None):
        self.collection.update({"_id": credentials_id}, {"$unset": {'error': ""}})




    # Service - legacy name
    def get_all_for_provider(self, provider_id=None):
        params = {'service': provider_id}

        result = self.collection.find(params)


        return result


cloud_credentials_model = CloudCredentialsModel()
