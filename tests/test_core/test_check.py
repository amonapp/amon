from amon.check import AmonCheckSystem
from nose.tools import *


class TestSystemCheck(object):

	def __init__(self):
		self.amon = AmonCheckSystem() 

	def test_memory(self):
		memory_dict = self.amon.get_memory_info()
		
		assert 'memfree' in memory_dict
		assert 'memtotal' in memory_dict
		assert 'swapfree' in memory_dict
		assert 'swaptotal' in memory_dict

		for v in memory_dict.values():
			assert isinstance(v, int)


	def test_disk(self):
		disk = self.amon.get_disk_usage()

		for k in disk:
			_dict = disk[k]

			assert 'used' in _dict
			assert 'percent' in _dict
			assert 'free' in _dict
			assert 'volume' in _dict
			assert 'total' in _dict


	def test_cpu(self):
		cpu = self.amon.get_cpu_utilization()

		assert 'idle' in cpu
		assert 'user' in cpu
		assert 'system' in cpu
		assert 'wait' in cpu 


		for v in cpu.values():
			assert isinstance(v, int)


	def test_loadavg(self):
		loadavg = self.amon.get_load_average()


		assert 'minute' in loadavg
		assert 'five_minutes' in loadavg
		assert 'fifteen_minutes' in loadavg
		assert 'scheduled_processes' in loadavg

		for v in loadavg.values():
			assert isinstance(v, int)
