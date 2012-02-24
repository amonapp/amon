from amon.system.collector import system_info_collector, process_info_collector
from nose.tools import eq_, assert_not_equal
import sys

class TestSystemCheck(object):

    def __init__(self):
        pass

    def test_memory(self):
        memory_dict = system_info_collector.get_memory_info()
        
        assert 'memfree' in memory_dict
        assert 'memtotal' in memory_dict
        assert 'swapfree' in memory_dict
        assert 'swaptotal' in memory_dict

        for v in memory_dict.values():
            assert isinstance(v, int)


    def test_disk(self):
        disk = system_info_collector.get_disk_usage()

        for k in disk:
            _dict = disk[k]

            assert 'used' in _dict
            assert 'percent' in _dict
            assert 'free' in _dict
            assert 'volume' in _dict
            assert 'total' in _dict


    def test_cpu(self):
        cpu = system_info_collector.get_cpu_utilization()

        # For debugging purposes only
        #print cpu
        #import subprocess
        #mpstat = subprocess.Popen(['iostat', '-c'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]
        #print mpstat

        assert 'idle' in cpu
        assert 'user' in cpu
        assert 'system' in cpu
        print cpu.values()

        for v in cpu.values():
            if sys.platform == 'darwin':
                assert isinstance(v, int)
            else:
                # Could be 1.10 - 4, 10.10 - 5, 100.00 - 6
                assert len(v) == 4 or len(v) == 5 or len(v) == 6


    def test_loadavg(self):
        loadavg = system_info_collector.get_load_average()

        assert 'minute' in loadavg
        assert 'five_minutes' in loadavg
        assert 'fifteen_minutes' in loadavg
        assert 'cores' in loadavg

        assert isinstance(loadavg['cores'], int)
        assert isinstance(loadavg['minute'], str)
        assert isinstance(loadavg['five_minutes'], str)
        assert isinstance(loadavg['fifteen_minutes'], str)

class TestProcessCheck(object):

    def __init__(self):
        self.process_checks = ('cron',) # something that's available in most linux distributions


    def test_process(self):
        for process in self.process_checks:
            process_dict = process_info_collector.check_process(process)
            
            assert 'memory' in process_dict
            assert 'cpu' in process_dict
            
