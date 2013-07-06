from amonone.web.apps.core.basemodel import BaseModel

class EmailModel(BaseModel):

	def __init__(self):
		super(EmailModel, self).__init__()
		self.collection = self.mongo.get_collection('email_settings')


	def save_email_details(self, data=None):
		self.collection.remove()
		self.collection.insert(data)

	def get_email_details(self):
		return self.collection.find_one()


class EmailRecepientModel(BaseModel):

	def __init__(self):
		super(EmailRecepientModel, self).__init__()
		self.collection = self.mongo.get_collection('email_recepients')

email_model = EmailModel()
email_recepient_model = EmailRecepientModel()
