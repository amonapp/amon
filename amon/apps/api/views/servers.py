import re

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response

from amon.utils.haiku import generate_haiku_name
from amon.apps.api.permissions import ApiKeyPermission
from amon.apps.servers.models import server_model
from amon.apps.alerts.models import alerts_model
from amon.apps.api.mixins import SaveRequestHistoryMixin
from amon.apps.tags.models import tags_model


class ServersListView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)


    def get(self, request):

        servers = server_model.get_all()

        filtered_servers = []
        if servers != None:
            for server in servers:
                filtered_servers.append({'name': server['name'], 
                    'key': server['key'],
                    'id': str(server['_id']),
                    'last_check': server.get('last_check'),
                    'provider': server.get('provider')}

                )


        status = settings.API_RESULTS['ok']

        return Response({'status': status, 'servers': filtered_servers})



class ServersCreateView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)


    def _create_server(self, name=None, key=None, tags=None):
        response = {}

        create_server = False

        if key:
            valid_key_format = bool(re.match('[a-z0-9]{32}$', key))

            if valid_key_format:
                create_server = True
            else:
                response['status'] = settings.API_RESULTS['unprocessable']
                response['error'] = 'Invalid server key. A random 32 character long, lowercase alpha numeric string is required.'
        
        else:
            create_server = True # Default

        if create_server:
            tag_ids = tags_model.create_and_return_ids(tags=tags)
            
            # Check if a server with this key already exists - provisioning tool, update agent:
            server = server_model.get_server_by_key(key)
        
            if server == None:
                server_key = server_model.add(name=name, account_id=settings.ACCOUNT_ID, key=key, tags=tag_ids)
            else:
                server_key = key

                data = {'name': name}
                # New tags sent throught the API
                if len(tag_ids) > 0:
                    data['tags'] = tag_ids

                server_model.update(data, server['_id'])
                name = server.get('name')
        
            response = {
                'status': settings.API_RESULTS['created'],
                'name': name,
                'server_key': server_key
            }

        return response

    def get(self, request):
        
        name = request.GET.get('name', generate_haiku_name())
        key = request.GET.get('key', False)
        tags = request.GET.getlist('tags', False)

        response = self._create_server(name=name, key=key, tags=tags)

        return Response(response)

    def post(self, request):
        response = {}
        create_server = False

        data = request.data

        name = data.get('name', generate_haiku_name())
        key = data.get('key', False)
        tags = data.get('tags', False)

        response = self._create_server(name=name, key=key, tags=tags)
        
        return Response(response)


class ServersDeleteView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)



    def get(self, request, server_id):    
        alerts_model.delete_server_alerts(server_id)
        server_model.delete(server_id)

        status = settings.API_RESULTS['ok']

        return Response({'status': status})
