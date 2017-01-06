from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import renderers

from amon.apps.api.permissions import ApiKeyPermission
# from amon.apps.cloudservers.apicalls import (
#     sync_amazon,
#     sync_rackspace,
#     sync_linode,
#     sync_digitalocean
# )

from amon.apps.servers.models import server_model

class CloudServersSyncView(APIView):
    permission_classes = (ApiKeyPermission,)

    def get(self, request, provider_id):

        account_id = settings.ACCOUNT_ID

        status = settings.API_RESULTS['ok']
        message = ""
        # if provider_id == 'amazon':
        #     sync_amazon(account_id=account_id)
        # elif provider_id == 'digitalocean':
        #     sync_digitalocean(account_id=account_id)
        # elif provider_id == 'rackspace':
        #     sync_rackspace(account_id=account_id)
        # elif provider_id == 'linode':
        #     sync_linode(account_id=account_id)
        # else:
        #     status = settings.API_RESULTS['not-found']

        if provider_id in ['amazon', 'rackspace', 'digitalocean', 'linode']:
            message = "{0} servers synced".format(provider_id.title())

        return Response({'status': status, "message": message})



class PlainTextRenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        return data.encode(self.charset)


def _get_server_key(instance_id=None):
    key = ''
    server =  server_model.collection.find_one({'instance_id': instance_id})
    if server:
        key = server.get('key')
    return key

class CloudServersGetServerKeyView(APIView):
    permission_classes = (ApiKeyPermission,)

    renderer_classes = (PlainTextRenderer,)
    
    def get(self, request, provider_id):
        key = ""
        params = request.query_params
        instance_id = params.get('instance_id')

        if provider_id in ['amazon', 'google', 'digitalocean']:
            key = _get_server_key(instance_id=instance_id)
        else:
            status = settings.API_RESULTS['not-found']

        return Response(key)
