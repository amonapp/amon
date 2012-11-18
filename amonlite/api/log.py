from amon.utils.dates import unix_utc_now
from amon.api.models import LogsAPIModel, CommonAPIModel

class Log(object):

    def __init__(self):
        self.model = LogsAPIModel()
        self.str = ""
        self.common_model = CommonAPIModel()

    def flatten_dict(self, d, parent_key=''):
        items = []
        for k, v in d.items():
            if isinstance(v, dict):
                self.str+=":%s" % k
                items.extend(self.flatten_dict(v, k).items())
            else:
                self.str+=":%s" % k
                items.append((k, v))
        
        return dict(items)  
    
    # Checks the tags in the database and adds them if they are new entries
    def check_tags(self, tags):

        if isinstance(tags, list):
            for el in tags:
                self.model.upsert_tag(el)
                        
        elif isinstance(tags, str) or isinstance(tags, unicode):
            self.model.upsert_tag(tags)

    def __call__(self, *args, **kwargs):

        log_dict = args[0]

        try:
            tags = log_dict.get('tags')
        except: 
            tags = None
        
        message = log_dict.get('message', '')

        now = unix_utc_now()

        self.check_tags(tags)

        entry = {'time': now, 'message': message, 'tags': tags}
        
        # Add the data to a separate field, for easy searching 
        if isinstance(message, dict):
             self.str = ""
             self.flatten_dict(message)
             _searchable = self.str
        elif isinstance(message, list):
            _searchable = ":".join(["%s" % el for el in message])
        else:
            _searchable = message
        
        entry['_searchable'] = _searchable

        self.model.save_log(entry)
        self.common_model.upsert_unread('logs')
