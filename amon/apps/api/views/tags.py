from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from amon.apps.api.permissions import ApiKeyPermission
from amon.apps.tags.models import tags_model, tag_groups_model
from amon.apps.api.mixins import SaveRequestHistoryMixin
from amon.apps.api.utils import dict_from_cursor

class TagsListView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)

    def get(self, request):
        tags = tags_model.get_all()
        filtered_tags = []
        for tag in tags:
            data = dict_from_cursor(data=tag, keys=['name', '_id'])
            group = tag.get('group')
            if group:
                data['group'] = dict_from_cursor(data=group, keys=['name', '_id'])
            
            filtered_tags.append(data)

        
        filtered_tags.sort(key=lambda e: e.get('group', {}).get('name'))

        status = settings.API_RESULTS['ok']

        return Response({'status': status, 'tags': filtered_tags})


class TagsUpdateView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)


    def post(self, request):
        data = JSONParser().parse(request)
        name = data.get('name')
        _id = data.get('id')
        group_id = data.get('group', {}).get('id', '')
        if name:
            update_dict = {'name': name, 'group_id': group_id}
            tags_model.update(update_dict, _id)
        
        status = settings.API_RESULTS['ok']
        return Response({'status': status})


class TagsCreateView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)


    def post(self, request):
        data = JSONParser().parse(request)
        name = data.get('name')
        group_id = data.get('group', {}).get('id')
        tag_id = tags_model.get_or_create_by_name(name=name)
        if group_id:
            tags_model.update({'group_id': group_id}, tag_id)

        new_tag = tags_model.get_by_id(tag_id)
        filtered_tag = dict_from_cursor(data=new_tag, keys=['name', '_id'])
        
        group = new_tag.get('group')
        if group != None:
             filtered_tag['group'] = dict_from_cursor(data=group, keys=['name', '_id'])
        
        status = settings.API_RESULTS['ok']
        return Response({'status': status, 'tag': filtered_tag})


class TagsDeleteView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)


    def post(self, request):    
        data = JSONParser().parse(request)
        tag_id = data.get('id')

        tags_model.delete(tag_id)

        status = settings.API_RESULTS['ok']

        return Response({'status': status})



class TagGroupsListView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)


    def get(self, request):
        groups = tag_groups_model.get_all()
        groups_list = []
        for g in groups:
            group = dict_from_cursor(data=g, keys=['name', '_id'])
            groups_list.append(group)


        status = settings.API_RESULTS['ok']

        return Response({'status': status, 'groups': groups_list})


class TagGroupsUpdateView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)


    def post(self, request):
        data = JSONParser().parse(request)
        name = data.get('name')
        _id = data.get('id')
        if name:
            tag_groups_model.update({'name': name}, _id)
        
        status = settings.API_RESULTS['ok']
        return Response({'status': status})


class TagGroupsCreateView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)


    def post(self, request):
        data = JSONParser().parse(request)
        name = data.get('name')
        _id = tag_groups_model.get_or_create_by_name(name=name)

        new_group = tag_groups_model.get_by_id(_id)
        new_group_dict = dict_from_cursor(data=new_group, keys=['name', '_id'])
        
        status = settings.API_RESULTS['ok']
        return Response({'status': status, 'group': new_group_dict})


class TagGroupsDeleteView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)


    def post(self, request):    
        data = JSONParser().parse(request)
        tag_id = data.get('id')

        tag_groups_model.delete(tag_id)

        status = settings.API_RESULTS['ok']

        return Response({'status': status})