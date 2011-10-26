import unittest
from amon.web.views import (
	Dashboard
)

class TestWebAppFunctions(unittest.TestCase):

	def test_me(self):
		index = Dashboard().index()
		print index
		assert False
