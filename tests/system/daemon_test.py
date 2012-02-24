# TODO Change this file every time there is a change in amond
from amon.core import settings
from amon.system.runner import runner
from amon.backends.mongodb import backend
import unittest
from nose.tools import eq_
import sys

class TestDaemon(unittest.TestCase):

    def setUp(self):
        backend.database = 'amon_test'



    def test_system(self):
        system_info = runner.system()
        
        cpu = backend.get_collection('cpu')
        cpu.remove()
        
        memory = backend.get_collection('memory')
        memory.remove()
        
        loadavg = backend.get_collection('loadavg')
        loadavg.remove()
        
        disk = backend.get_collection('disk')
        disk.remove()
        
        network = backend.get_collection('network')
        network.remove()
        
        backend.store_entries(system_info)

        eq_(1, cpu.count())
        eq_(1, memory.count())
        eq_(1, loadavg.count())
        eq_(1, disk.count())
        if sys.platform != 'darwin':
            eq_(1, network.count())
        


    def test_processes(self):
        process_info = runner.processes()
        process_checks = settings.PROCESS_CHECKS
        
        
        for process in process_checks:
            db = backend.get_collection(process)
            db.remove()
        
        backend.store_entries(process_info)

        for process in process_checks:
            db = backend.get_collection(process)
            eq_(1, db.count())
