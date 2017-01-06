from amon.apps.core.basemodel import BaseModel

class NotificationsModel(BaseModel):

    def __init__(self):
        super(NotificationsModel, self).__init__()
        self.collection = self.mongo.get_collection('notifications_settings')


    def save(self, data=None, provider_id=None):
        data['provider_id'] = provider_id
        self.collection.insert(data)
        self.collection.ensure_index('provider_id', background=True)

    def update(self, data=None, id=None):
        id = self.object_id(id)

        self.collection.update({"_id": id}, {"$set": data}, upsert=True)
        self.collection.ensure_index('provider_id', background=True)


    # Used in alerts and health checks
    def get_list_of_strings_to_mongo_objects(self, notifications_list=None):
        result = []
        if len(notifications_list) > 0:
            for x in notifications_list:
                split_provider_id = x.split(':')  # email:id

                if len(split_provider_id) == 2:
                    _id = split_provider_id[1]
                    cursor = self.get_by_id(_id)
                    if cursor:  # Append if exists
                        result.append(cursor)


        return result


    def get_all_formated(self):
        result = self.get_all(sort_by='provider_id')

        result_list = []

        for r in result.clone():
            r['formated_id'] = "{0}:{1}".format(r.get('provider_id'), r.get('_id'))
            result_list.append(r)

        return result_list


    def get_all_for_provider(self, provider_id=None):
        params = {'provider_id': provider_id}

        result = self.collection.find(params)


        return result


notifications_model = NotificationsModel()
