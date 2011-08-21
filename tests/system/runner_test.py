from nose.tools import *
from amon.system.runner import runner


class TestRunner(object):

	def test_system_run(self):
		system_test = runner.system()

		assert isinstance(system_test, dict)
		assert 'network' in system_test
		assert 'memory' in system_test
		assert 'cpu' in system_test
		assert 'disk' in system_test
		assert 'loadavg' in system_test

	def test_system_empty(self):
		empty = runner.empty()
		assert 'network' in empty
		assert 'memory' in empty
		assert 'cpu' in empty
		assert 'disk' in empty
		assert 'loadavg' in empty

	def test_process_run(self):
		processes = runner.processes()
		assert isinstance(processes, dict)


