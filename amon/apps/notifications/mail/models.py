from amon.apps.core.basemodel import BaseModel
from django.conf import settings

class EmailModel(BaseModel):

    def __init__(self):
        super(EmailModel, self).__init__()
        self.collection = self.mongo.get_collection('email_settings')


    def save_email_settings(self, data=None):
        self.collection.remove()
        self.collection.insert(data)

    def get_email_settings(self):
        email_settings = self.collection.find_one()
        if email_settings == None:
            email_settings = {}

        if settings.SMTP != False:
            email_settings = {
                'host': settings.SMTP.get('host'),
                'port': settings.SMTP.get('port'),
                'username': settings.SMTP.get('username', False),
                'password': settings.SMTP.get('password', False),
                'use_tls': settings.SMTP.get('use_tls', False),
                'sent_from': settings.SMTP.get('sent_from', 'alertbot@amon.mailgun.org'),
            }
            

        return email_settings


email_model = EmailModel()
