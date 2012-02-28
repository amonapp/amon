from amon.utils.dates import *
from nose.tools import eq_
import datetime
import pytz
import unittest


class TestDates(unittest.TestCase):

    def test_datestring_to_utc_datetime(self):
        # UTC
        result = datestring_to_utc_datetime("25-02-2012-00:00",_timezone='Europe/London') 
        eq_(result, datetime.datetime(2012, 2, 25, 0, 0, tzinfo=pytz.UTC))

        # UTC
        result = datestring_to_utc_datetime("25-02-2012-00:00",_timezone='UTC') 
        eq_(result, datetime.datetime(2012, 2, 25, 0, 0, tzinfo=pytz.UTC))

        # +2 ( 0:00 in Sofia is 22:00 UTC )
        result = datestring_to_utc_datetime("25-02-2012-00:00", _timezone='Europe/Sofia') 
        eq_(result, datetime.datetime(2012, 2, 24, 22, 0, tzinfo=pytz.UTC))

        # -7 ( 0:00 in Edmonton is 07:00 UTC )
        result = datestring_to_utc_datetime("25-02-2012-00:00", _timezone='America/Edmonton') 
        eq_(result, datetime.datetime(2012, 2, 25, 7, 0, tzinfo=pytz.UTC))

        # +8 ( 0:00 in Hong Kong is 16:00 UTC )
        result = datestring_to_utc_datetime("25-02-2012-00:00", _timezone='Asia/Hong_Kong') 
        eq_(result, datetime.datetime(2012, 2, 24, 16, 0, tzinfo=pytz.UTC))

    def test_datetime_to_unixtime(self):
        date = datetime.datetime(2012, 2, 25, 0, 0, tzinfo=pytz.UTC) 
        result = datetime_to_unixtime(date)
        eq_(result, 1330128000)

    def test_utc_unixtime_to_localtime(self):
        # 1340000000 -> Mon, 18 Jun 2012 06:13:20 GMT 
        # UTC+3 -> Eastern Europe summer time 
        result = utc_unixtime_to_localtime(1340000000, _timezone='Europe/Sofia') 
        eq_(result, 1340010800) 

        # UTC+5  
        result = utc_unixtime_to_localtime(1340000000, _timezone='Antarctica/Mawson') 
        eq_(result, 1340018000) 
        
        # UTC-6 
        result = utc_unixtime_to_localtime(1340000000, _timezone='America/Belize') 
        eq_(result, 1339978400) 


    def test_localtime_utc_timedelta(self):
        # +5 ( 0:00 in Mawson is 19:00 UTC )
        result = localtime_utc_timedelta(_timezone='Antarctica/Mawson') 
        eq_(result, ('negative', 18000))

        # +2 ( 0:00 in Sofia is 22:00 UTC )
        result = localtime_utc_timedelta(_timezone='Europe/Sofia') 
        eq_(result, ('negative', 7200))

        # -7 ( 0:00 in Edmonton is 07:00 UTC )
        result = localtime_utc_timedelta(_timezone='America/Edmonton') 
        eq_(result, ('positive', 25200))

        # UTC
        result = localtime_utc_timedelta(_timezone='UTC') 
        eq_(result, ('positive', 0))

    def test_utc_now_to_localtime(self):
        # +5 ( 0:00 in Mawson is 19:00 UTC )
        utc_now = unix_utc_now()
        result = utc_now_to_localtime(_timezone='Antarctica/Mawson')
        eq_(result, utc_now+18000)

        # +2 ( 0:00 in Sofia is 22:00 UTC )
        utc_now = unix_utc_now()
        result = utc_now_to_localtime(_timezone='Europe/Sofia')
        eq_(result, utc_now+7200)


    def test_unix_utc_now(self):
        result = unix_utc_now()
        assert isinstance(result, int)
