from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status

from amon.apps.servers.models import server_model

from amon.apps.api.throttle import CheckPeriodThrottle
from amon.apps.api.permissions import ApiKeyPermission
from amon.apps.notifications.sender import send_notifications
from amon.apps.api.models import api_model

class CheckIpAddressView(APIView):


    def get(self, request):

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')


        return Response({'ip': ip})


class TestView(APIView):

    def get(self, request, server_key):
        server = server_model.get_server_by_key(server_key)
        response_status = status.HTTP_200_OK if server else status.HTTP_403_FORBIDDEN

        return Response(status=response_status)

    def post(self, request, server_key):
        server = server_model.get_server_by_key(server_key)
        response_status = status.HTTP_200_OK if server else status.HTTP_403_FORBIDDEN

        return Response(status=response_status)


# New golang agent data, format before saving it
class SystemDataView(APIView):
    permission_classes = (ApiKeyPermission,)

    def post(self, request):

        status = settings.API_RESULTS['not-found']
        data = JSONParser().parse(request)

        host_data = data.get('host')
        machine_id = host_data.get('machineid')
        hostname = host_data.get('host')

        # Cloud synced servers
        instance_id = host_data.get('instance_id', "")


        server = server_model.get_or_create_by_machine_id(machine_id=machine_id,
            hostname=hostname,
            instance_id=instance_id)

        api_model.save_data_to_backend(server=server, data=data)

        # Update host data
        server_meta = {
            'ip_address': host_data.get('ip_address'),
            'distro': host_data.get('distro', {}),
        }

        server_model.update(server_meta, server['_id'])

        if settings.DEBUG is True:
            send_notifications()

        status = settings.API_RESULTS['ok']


        return Response({'status': status})


class LegacySystemDataView(APIView):

    throttle_classes = (CheckPeriodThrottle,)

    def post(self, request, server_key):

        status = settings.API_RESULTS['not-found']
        data = JSONParser().parse(request)

        if request.server:
            api_model.save_data_to_backend(server=request.server, data=data)

            if settings.DEBUG is True:
                send_notifications()

            status = settings.API_RESULTS['ok']

        return Response({'status': status})


class SystemInfoView(APIView):

    def post(self, request, server_key):
        status = settings.API_RESULTS['not-found']

        data = JSONParser().parse(request)
        server = server_model.get_server_by_key(server_key)

        valid_keys = ['ip_address', 'processor', 'distro', 'uptime']
        if server:

            if set(data.keys()).issubset(valid_keys):
                server_model.update(data, server['_id'])


            status = settings.API_RESULTS['ok']

        return Response({'status': status})
