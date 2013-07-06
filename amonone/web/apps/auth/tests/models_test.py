import unittest
from nose.tools import eq_
from amonone.web.apps.auth.models import UserModel

class TestUserModel(unittest.TestCase):

    def setUp(self):
        self.model = UserModel()


    def test_create_user(self):
        self.model.collection.remove()
        self.model.create_user({'username': "test", 'password': '1234'})
        eq_(self.model.collection.count(),1)


    def test_check_user(self):
        self.model.collection.remove()
        user_dict = {"username": "test", "password": "1234"}
        self.model.create_user(user_dict)

        result = self.model.check_user({"username": "test", "password": "1234"})

        # username, pass, _id
        eq_(len(result), 3)

        result = self.model.check_user({"username": "noname","password": ""})

        eq_(result, {})


    def test_username_exists(self):
        self.model.collection.remove()

        result = self.model.username_exists("test")
        eq_(result, 0)

        self.model.create_user({'username': "test", 'password': '1234'})

        result = self.model.username_exists("test")
        eq_(result, 1)