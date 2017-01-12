import unittest

from django.contrib.auth import get_user_model
User = get_user_model()

from amon.apps.api.models import api_key_model
from amon.apps.api.utils import generate_api_key


class APIKeyModelTest(unittest.TestCase):

    def setUp(self):
        self.collection = api_key_model.collection

    def tearDown(self):
        self.collection.remove()
        

    def _cleanup(self):
        self.collection.remove()



    def create_test(self):
        self._cleanup()

        key = generate_api_key()
            
        api_key_model.add({'key': key})
        params = {'key': key}
        result = api_key_model.get_one(params=params)

        assert result['key'] == key


        self._cleanup()

        