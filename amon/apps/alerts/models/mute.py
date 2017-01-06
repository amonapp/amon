from datetime import datetime, timedelta

from amon.apps.core.basemodel import BaseModel
from amon.utils.dates import datetime_to_unixtime
from amon.apps.tags.models import tags_model
from amon.apps.servers.models import server_model

class AlertMuteServersModel(BaseModel):

    def __init__(self):
        super(AlertMuteServersModel, self).__init__()
        self.collection = self.mongo.get_collection('alerts_muted_servers')


    def check_if_server_is_muted(self, server=None):
        muted = False
        cursor = super(AlertMuteServersModel, self).get_all()

        server_id = str(server.get('_id'))
        server_tags = server.get('tags', [])
        server_tags = [str(t) for t in server_tags]

        for r in cursor:
            tags = r.get('tags', [])
            tags = [str(t) for t in tags]
            mute_server_id = str(r.get('server'))

            # Check tags first
            if len(server_tags) > 0 and len(tags) > 0:
                muted = set(tags).issubset(server_tags)

            # Don't overwrite
            if muted == False:
                # Check IDS now
                muted = True if mute_server_id == server_id else False


            # Finally check for global mute, no tags
            if mute_server_id == 'all' and len(tags) == 0:
                muted = True

        return muted
        


    def get_all(self):
        result_list = []
        result = super(AlertMuteServersModel, self).get_all()
        for r in result:
            tags = r.get('tags', [])
            r['tags'] = [tags_model.get_by_id(x) for x in tags]
            r['server'] = server_model.get_by_id(r.get('server'))
            
            
            result_list.append(r)


        return result_list


    def save(self, data=None):
        period = int(data.get('period'))

        if period > 0:
            expire_at = datetime.utcnow() + timedelta(hours=period)

            data['expires_at_utc'] = datetime_to_unixtime(expire_at)
            data['expires_at'] = expire_at 

        self.collection.insert(data)
        self.collection.ensure_index([('expires_at', 1)], expireAfterSeconds=0)
