from django.test import TestCase

from nose.tools import eq_

from amon.apps.plugins.helpers import (
    flat_to_tree_dict_helper,
    replace_underscore_with_dot_helper
)


class TestPluginHelpers(TestCase):

    def flat_to_tree_dict_helper_test(self):
        data = {'t': 1, 'count.test': 2, 'second.test': 4, 'more.tests': 5}
        formated_data = flat_to_tree_dict_helper(data)


        eq_(formated_data, {'count': {'test': 2}, 'second': {'test': 4}, 't': 1, 'more': {'tests': 5}})


        data = {'t': 1, 'count.test': 2, 'count.test.testmore': 422, 'second.test': 4, 'more.tests': 5}
        formated_data = flat_to_tree_dict_helper(data)

        eq_(formated_data, {'count': {'test': 2, 'test_testmore': 422}, 'second': {'test': 4}, 't': 1, 'more': {'tests': 5}})


        data = {"name.first.name": 'Martin', "name.last.name": "Rusev"}
        formated_data = flat_to_tree_dict_helper(data)

        eq_(formated_data, {'name': {'first_name': 'Martin', 'last_name': 'Rusev'}})

        

    def replace_underscore_with_dot_helper_test(self):
        data = {'t': 1, 'count_test': 2, 'second_test': 4, 'third_level_test': 5}

        formated_data = replace_underscore_with_dot_helper(data)

        assert set(formated_data) == set({'t': 1, 'count.test': 2, 'second.test': 4, 'third.level.test': 5})


        data = {'t': 1, 'count_test_deeper': 2, 'second_test': 4, 'more_tests': 5}

        formated_data = replace_underscore_with_dot_helper(data)

        eq_(set(formated_data), set({'t': 1, 'count.test.deeper': 2, 'second.test': 4, 'more.tests': 5}))