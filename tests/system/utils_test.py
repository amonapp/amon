from amon.system.utils import *
from nose.plugins.skip import SkipTest
import sys

class TestSystemUtils(object):

    def test_disk_volumes(self):
        volumes = get_disk_volumes()
    
        assert isinstance(volumes, list)
        for v in volumes:
            assert isinstance(v, str)

    def test_network_interfaces(self):
        if sys.platform == 'darwin':
            raise SkipTest

        interfaces = get_network_interfaces()

        assert isinstance(interfaces, list)

        for v in interfaces:
            assert isinstance(v, str)
    

