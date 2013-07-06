from hashlib import sha1
from amonone.web.apps.core.basemodel import BaseModel

class ServerModel(BaseModel):

	def __init__(self):
		super(ServerModel, self).__init__()
		self.collection = self.mongo.get_collection('server')


server_model = ServerModel()
