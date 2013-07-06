from amonone.web.apps.core.basemodel import BaseModel

class SMSModel(BaseModel):

	def __init__(self):
		super(SMSModel, self).__init__()
		self.collection = self.mongo.get_collection('sms_settings')

	def save(self, data=None):
		self.collection.remove()
		self.collection.insert(data)

	def get(self):
		return self.collection.find_one()

class SMSRecepientModel(BaseModel):

	def __init__(self):
		super(SMSRecepientModel, self).__init__()
		self.collection = self.mongo.get_collection('sms_recepients')

		

sms_model = SMSModel()
sms_recepient_model = SMSRecepientModel()