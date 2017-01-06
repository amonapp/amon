from amon.apps.core.basemodel import BaseModel
from django.conf import settings

class EmailRecepientModel(BaseModel):

    def __init__(self):
        super(EmailRecepientModel, self).__init__()
        self.collection = self.mongo.get_collection('email_recepients')


    def get_all(self):
        
        count = self.collection.find().count()

        if count == 0:
            return None
        else:
            return self.collection.find(sort=[("name", self.asc)])


    def add_initial_data(self, email=None):
        count = self.collection.find().count()

        if count == 0:
            data = {'account_id': settings.ACCOUNT_ID, 'email': email}
            self.collection.insert(data)
        

class WebHooksModel(BaseModel):

    def __init__(self):
        super(WebHooksModel, self).__init__()
        self.collection = self.mongo.get_collection('webhooks')



webhooks_model = WebHooksModel()
email_recepient_model = EmailRecepientModel()