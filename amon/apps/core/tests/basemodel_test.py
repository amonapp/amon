import unittest
from nose.tools import eq_

from amon.apps.core.basemodel import BaseModel

class BaseModelTest(unittest.TestCase):

    def setUp(self):
        self.model = BaseModel()
        

    def rename_keys_test(self):
        original_dict = {'inbound': 1, 'outbound': 2, 't':1, 'server_id': 4}
        new_keys = {'inbound': 'i', 'outbound': 'o'}

        result = self.model.rename_keys(original_dict, new_keys)

        eq_(result, {'i': 1, 'o': 2, 't': 1, 'server_id': 4})


    def format_float_test(self):
        result = self.model.format_float(2)

        eq_(result, 2.0)

        result = self.model.format_float("23.4")
        eq_(result, 23.4)

        result = self.model.format_float("test")
        eq_(result, False)
