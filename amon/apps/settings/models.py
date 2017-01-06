from amon.apps.core.basemodel import BaseModel


class DataRetentionModel(BaseModel):

    def __init__(self):
        super(DataRetentionModel, self).__init__()
        self.collection = self.mongo.get_collection('data_retention_settings')

data_retention_model = DataRetentionModel()