import unittest
from amon.web.template import *
from nose.tools import eq_

class TestTemplateFilters(unittest.TestCase):

    def test_dateformat(self):
        date = dateformat(1319737106)
        eq_('27-10-2011-17:38', date)


    def test_timeformat(self):
        time = timeformat(1319737106)
        eq_('17:38', time)

    def test_date_to_js(self):
        date = date_to_js(1319737106)
        eq_('2011,9, 27, 17, 38', date)


    def test_to_int(self):
        _int = to_int('testme2')
        eq_(_int, 2)

    def test_clean_string(self):
        string = clean_string('24.5MB')
        eq_(string, 24.5)

    
    def test_progress_width_percent(self):
        full_container = progress_width_percent(100, container_type='full' )
        eq_(full_container, '500px')

        full_container = progress_width_percent(50, container_type='full' )
        eq_(full_container, '250px')

        full_container = progress_width_percent(0, container_type='full' )
        eq_(full_container, '0px; border:0px')

        container = progress_width_percent(100, container_type='medium' )
        eq_(container, '245px')

        container = progress_width_percent(50, container_type='medium' )
        eq_(container, '122px')

        container = progress_width_percent(0, container_type='medium' )
        eq_(container, '0px; border:0px')

        container = progress_width_percent(100, container_type='small' )
        eq_(container, '145px')

        container = progress_width_percent(50, container_type='small' )
        eq_(container, '72px')

    def test_progress_width(self):
        full_container = progress_width(300, 300, container_type='full' )
        eq_(full_container, '500px')

        full_container_50 = progress_width(150, 300, container_type='full' )
        eq_(full_container_50, '250px')


        full_container_0 = progress_width(0, 300, container_type='full' )
        eq_(full_container_0, '0px; border:0px')


        medium_container = progress_width(300, 300, container_type='medium' )
        eq_(medium_container, '245px')

        medium_container_50 = progress_width(150, 300, container_type='medium' )
        eq_(medium_container_50, '122px')

        medium_container_0 = progress_width(0, 300, container_type='medium' )
        eq_(medium_container_0, '0px; border:0px')


        small_container = progress_width(300, 300, container_type='small' )
        eq_(small_container, '145px')


        small_container_50 = progress_width(150, 300, container_type='small' )
        eq_(small_container_50, '72px')

        small_container_0 = progress_width(0, 300, container_type='small' )
        eq_(small_container_0, '0px; border:0px')

    def test_progress_width_with_zeroes(self):
        empty_container_full = progress_width(0,0, container_type='full' )
        eq_(empty_container_full, '0px; border:0px')


        empty_container_medium = progress_width(0,0, container_type='medium' )
        eq_(empty_container_medium, '0px; border:0px')


        empty_container_small = progress_width(0,0, container_type='small' )
        eq_(empty_container_small, '0px; border:0px')


    def test_value_bigger_than_total(self):
        container_full = progress_width(600,0, container_type='full' )
        eq_(container_full, '500px')


    def test_with_big_numbers(self):
        container_full = progress_width(12332323600,3434344, container_type='full')
        eq_(container_full, '500px') # Value bigger than total - container is 100%

        container = progress_width(9,12233332, container_type='full')
        eq_(container, '0px; border:0px') 

        container_full = progress_width(1232,34343, container_type='full')
        eq_(container_full, '15px') 


    def test_url(self):
        _url = url('more', 'and', 'even', 'more')
        eq_(_url, 'more/and/even/more')


    def test_base_url(self):
        _base_url = base_url()
        assert isinstance(_base_url, str)

    def test_check_additional_data(self):
        ignored_dicts = [{'occurrence': 12223323}, {'occurrence': 1212121221}]
        check_ignored_dicts = check_additional_data(ignored_dicts)
        eq_(check_ignored_dicts, None)

        true_dicts = [{'occurrence': 12223323, 'test': 'me'}, {'occurrence': 1212121221}]
        check_true_dicts = check_additional_data(true_dicts)
        eq_(check_true_dicts, True)

    def test_cleanup_string(self):
        string = '//test---/'
        clean = clean_slashes(string)
        eq_(clean, 'test')

    def test_query_dict(self):
        base_url = 'local'
        
        # Single parameter with single value
        uri = query_dict(base_url, {'tags': ['test']},1)
        eq_(uri, 'local?tags=test&page=1')

        # Single parameter with multiple values
        uri = query_dict(base_url, {'tags': ['test', 'more']},1)
        eq_(uri, 'local?tags=test&tags=more&page=1')

        # Single parameter, no page, no values
        uri = query_dict(base_url, {'tags': []})
        eq_(uri, 'local')

        # Single parameter, page , no values
        uri = query_dict(base_url, {'tags': []},1)
        eq_(uri, 'local?page=1')
        
        # Multiple paramaters with multiple values
        uri = query_dict(base_url, {'tags': ['test', 'more'], 'query': ['test','me']},1)
        eq_(uri, 'local?query=test&query=me?tags=test&tags=more&page=1')
        
        # Single parameter, page , value is None
        uri = query_dict(base_url, {'tags': None },1)
        eq_(uri, 'local?page=1')

