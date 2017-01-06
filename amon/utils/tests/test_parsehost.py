import unittest
from nose.tools import eq_
from amon.utils.parsehost import parsehost


class ParseHostTest(unittest.TestCase):


    def test_parsehost(self):
        # Test domain
        result = parsehost('http://amon.cx')

        assert result.__dict__ == {'scheme': 'http', 'host': 'http://amon.cx', 'hostname': 'amon.cx', 'port': 80}

        # Test domain
        result = parsehost('amon.cx')

        assert result.__dict__ == {'scheme': 'http', 'host': 'http://amon.cx', 'hostname': 'amon.cx', 'port': 80}
        
        # Test HTTPS
        result = parsehost('https://amon.cx')
        assert result.__dict__ == {'scheme': 'https', 'host': 'https://amon.cx', 'hostname': 'amon.cx', 'port': 443}


        # Test Subdomain
        result = parsehost('https://simplistic.amon.cx')
        assert result.__dict__ == {'scheme': 'https', 'host': 'https://simplistic.amon.cx', 'hostname': 'simplistic.amon.cx', 'port': 443}


        # Test Subdomain
        result = parsehost('http://simplistic.amon.cx')
        assert result.__dict__ == {'scheme': 'http', 'host': 'http://simplistic.amon.cx', 'hostname': 'simplistic.amon.cx', 'port': 80}


        # Test Custom port
        result = parsehost('http://simplistic.amon.cx:900')
        assert result.__dict__ == {'scheme': 'http', 'host': 'http://simplistic.amon.cx', 'hostname': 'simplistic.amon.cx', 'port': 900}