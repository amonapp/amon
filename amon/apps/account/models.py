import random 
import string

from amon.apps.core.basemodel import BaseModel


class AccountModel(BaseModel):

    def __init__(self):
        super(AccountModel, self).__init__()


class UserPreferencesModel(BaseModel):

    def __init__(self):
        super(UserPreferencesModel, self).__init__()
        self.collection = self.mongo.get_collection('user_preferences')


    def save_preferences(self, data=None, user_id=None):
        self.collection.update({'user_id': user_id}, {"$set": data}, upsert=True)

        self.collection.ensure_index([('user_id', self.desc)], background=True)

    def get_preferences(self, user_id=None):
        result = self.collection.find_one({'user_id': user_id})

        result = {} if result is None else result
        
        return result


class ForgottenPasswordTokensModel(BaseModel):


    def __init__(self):
        super(ForgottenPasswordTokensModel, self).__init__()
        self.collection = self.mongo.get_collection('forgotten_pass_tokens')

    def generate_token(self, size=30, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))


    def set_token(self, email=None):
        token = self.generate_token()
        data = {'token': token}

        self.collection.update({'email': email}, {"$set": data}, upsert=True)

        self.collection.ensure_index([('token', self.desc)], background=True)

        return token

forgotten_pass_tokens_model = ForgottenPasswordTokensModel()
user_preferences_model = UserPreferencesModel()
account_model = AccountModel()