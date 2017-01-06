from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status

from amon.apps.servers.models import server_model


class TelegrafDataView(APIView):

    def get(self, request, server_key):
        server = server_model.get_server_by_key(server_key)
        response_status = status.HTTP_200_OK if server else status.HTTP_403_FORBIDDEN

        return Response(status=response_status)

    def post(self, request, server_key):
        server = server_model.get_server_by_key(server_key)
        response_status = status.HTTP_200_OK if server else status.HTTP_403_FORBIDDEN
        
        return Response(status=response_status) 