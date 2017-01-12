from django.contrib.auth.decorators import login_required
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from amon.apps.alerts.models import alerts_api_model
from amon.apps.healthchecks.models import health_checks_api_model


@login_required
@api_view(['POST', 'GET'])
def ajax_get_metrics(request):
    status = settings.API_RESULTS['ok']
    
    if request.method == 'POST':
        data = request.data
        server_id = data.get('server_id')
    else:
        server_id = request.GET.get('server_id')

    if server_id == 'all':
        result = alerts_api_model.get_global_metrics()
    else:
        result = alerts_api_model.get_server_metrics(server_id=server_id)
    

    return Response(result)



@login_required
@api_view(['POST', 'GET'])
def ajax_get_health_check_commands(request):
        
    result = []
    if request.method == 'POST':
        data = request.data
        server_id = data.get('server_id')
    else:
        server_id = request.GET.get('server_id')

    if server_id == 'all':
        result = health_checks_api_model.get_unique_commands()
    else:
        cursor = health_checks_api_model.get_commands_for_server(server_id=server_id)
        for r in cursor.clone():
            params = r.get("params", False)
            params = "" if params is False else params
            command = "{0} {1}".format(r.get("command"), params)
            result.append(command)


    return Response(result)


# AJAX 
@login_required
@api_view(['POST', 'GET'])
def ajax_get_health_check_get_params_for_command(request):
    if request.method == 'POST':
        data = request.data
        command = data.get('command')
    else:
        command = request.GET.get('command')

    result = health_checks_api_model.get_params_for_command(command_string=command)

    return Response(result)

