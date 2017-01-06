import unittest

from nose.tools import eq_

from django.contrib.auth import get_user_model
User = get_user_model()

from amon.apps.tags.models import tags_model, tag_groups_model


class TagsModelTest(unittest.TestCase):

    def setUp(self):
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        
        self.account_id = 1


    def tearDown(self):
        self.user.delete()
        User.objects.all().delete()
        
        
    
    def _cleanup(self):
        tags_model.collection.remove()
        tag_groups_model.collection.remove()


    # def get_for_group_test(self):
    #     assert False


    def get_list_of_tags_test(self):
        self._cleanup()

        tags = {'rds': 'value', 'ebs': 'volume'}
        first_result = tags_model.create_and_return_ids(tags)

        result = tags_model.get_list_of_tags(first_result)


        for r in result:
            assert r['full_name'] in ['rds.value', 'ebs.volume']


        result = tags_model.get_list_of_tags(first_result, to_dict=True)

        for r in result:
            assert type(r['group_id']) is str
        


    def create_and_return_ids_test(self):
        self._cleanup()
        
        # Group
        tags = {'rds': 'value', 'ebs': 'volume'}
        first_result = tags_model.create_and_return_ids(tags)


        assert len(first_result) == 2
        assert tag_groups_model.collection.find().count() == 2
        second_result = tags_model.create_and_return_ids(tags)


        assert len(second_result) == 2
        assert tag_groups_model.collection.find().count() == 2
        assert first_result == second_result


        self._cleanup()

        # List
        tags = ['rds', 'ebs:value']
        first_result = tags_model.create_and_return_ids(tags)


        assert len(first_result) == 2
        assert tag_groups_model.collection.find().count() == 1
        second_result = tags_model.create_and_return_ids(tags)


        assert len(second_result) == 2
        assert tag_groups_model.collection.find().count() == 1
        assert first_result == second_result


    def get_or_create_test(self):
        self._cleanup()

        result = tags_model.get_or_create(name='testmeagain')

        assert tags_model.collection.find().count() == 1

        result = tags_model.get_or_create(name='testmeagain')

        assert tags_model.collection.find().count() == 1
        

    # def get_or_create_by_name_test(self):
    #     assert False