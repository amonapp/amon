import requests
import unittest
from nose.tools import eq_
from amonone.core import settings
from amonone.web.template import base_url
from amonone.web.apps.core.models import server_model
from amonone.web.utils import generate_random_string

# class TestSettings(unittest.TestCase):

# 	def setUp(self):
# 		self.base_url = base_url()


# 	def test_server_settings(self):
# 		url = "{0}/settings/servers".format(self.base_url)
# 		server_model.collection.remove()

# 		response = requests.get(url)
# 		eq_(response.status_code, 200)


# 		# Add 
# 		server_name = generate_random_string()
# 		response = requests.post(url, {"name": server_name})

# 		server = server_model.collection.find_one()
# 		eq_(server['name'], server_name)
# 		eq_(response.status_code, 200)


# 		# Edit
# 		edit_url = "{0}/edit/{1}".format(url, server['_id'])
# 		new_server_name = generate_random_string()
		
# 		response = requests.get(edit_url)
# 		eq_(response.status_code, 200)

# 		response = requests.post(edit_url, {"name": new_server_name})
# 		server = server_model.collection.find_one()
# 		eq_(server['name'], new_server_name)
# 		eq_(response.status_code, 200)


# 		# Delete
# 		delete_url = "{0}/delete/{1}".format(url, server['_id'])
# 		response = requests.get(delete_url)
# 		eq_(response.status_code, 200)
# 		eq_(0, server_model.collection.count())


