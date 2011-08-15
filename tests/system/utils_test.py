from amon.system.utils import *
from nose.tools import *

class TestSystemUtils(object):

	def test_disk_volumes(self):
		volumes = get_disk_volumes()
	
		assert isinstance(volumes, list)
		for v in volumes:
			assert isinstance(v, str)

	def test_network_interfaces(self):
		interfaces = get_network_interfaces()

		assert isinstance(interfaces, list)

		for v in interfaces:
			assert isinstance(v, str)
	

