from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser


from amon.apps.api.permissions import ApiKeyPermission
from amon.apps.healthchecks.models import health_checks_model
from amon.apps.api.mixins import SaveRequestHistoryMixin


class HealthChecksListView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)


    def get(self, request):

        checks = health_checks_model.get_all()

        checks_json = []
        for a in checks:
            check_dict = {
                'id': str(a.get('_id')), 
                'paused': a.get('paused', False),
                'last_executed': a.get('last_executed'),
                'execute_every': a.get('execute_every')
            }

            command = a.get('command')
            if command:
                check_dict['command'] = command
            filename = a.get('filename')
            if filename:
                check_dict['filename'] = filename
            
            params = a.get('params')
            if params:
                check_dict['params'] = params

            result = a.get('result')
            if len(result) > 0:
                check_dict['result'] = result

            checks_json.append(check_dict)


        status = settings.API_RESULTS['ok']

        return Response({'status': status, 'checks': checks_json})