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
		eq_(string, '24.5')


	def test_progress_width(self):
		full_container = progress_width(300, 300, container_type='full' )
		eq_(full_container, '500px')

		full_container_50 = progress_width(150, 300, container_type='full' )
		eq_(full_container_50, '250px')


		medium_container = progress_width(300, 300, container_type='medium' )
		eq_(medium_container, '245px')

		medium_container_50 = progress_width(150, 300, container_type='medium' )
		eq_(medium_container_50, '122px')

		small_container = progress_width(300, 300, container_type='small' )
		eq_(small_container, '145px')


		small_container_50 = progress_width(150, 300, container_type='small' )
		eq_(small_container_50, '72px')


	def test_url(self):
		_url = url('more', 'and', 'even', 'more')
		eq_(_url, 'more/and/even/more')


	def test_check_additional_data(self):
		ignored_dicts = [{'occurrence': 12223323}, {'occurrence': 1212121221}]
		check_ignored_dicts = check_additional_data(ignored_dicts)
		eq_(check_ignored_dicts, None)

		true_dicts = [{'occurrence': 12223323, 'test': 'me'}, {'occurrence': 1212121221}]
		check_true_dicts = check_additional_data(true_dicts)
		eq_(check_true_dicts, True)
