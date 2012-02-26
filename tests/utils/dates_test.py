from amon.utils.dates import *
import unittest


class TestDates(unittest.TestCase):

    def test_unix_utc_now(self):
        result = unix_utc_now()
        assert isinstance(result, int)
