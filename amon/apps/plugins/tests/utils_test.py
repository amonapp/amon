from django.test import TestCase
from nose.tools import *

from amon.apps.plugins.utils import (
    get_find_by_string_param
)


class TestGetFindByString(TestCase):

    
    def get_find_by_string_param_test(self):

        # Default 
        result = get_find_by_string_param()
        assert result == 'query'


        result  = get_find_by_string_param(table_data_type='not_found')
        assert result == 'data'


        result  = get_find_by_string_param(table_data_type='tables_size', name='boo')
        assert result == 'query' # Default


        result  = get_find_by_string_param(table_data_type='tables_size', name='mongo')
        assert result == 'ns' # Default

        result  = get_find_by_string_param(table_data_type='tables_size', name='mysql')
        assert result == 'full_name' # Default

