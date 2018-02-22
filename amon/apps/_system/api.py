from django.contrib.auth.decorators import login_required

from amon.apps.system.views import get_system_data_after
from rest_framework.decorators import api_view
from rest_framework.response import Response



@login_required
@api_view(['GET'])
def ajax_get_data_after(request):
    server_id = request.GET.get('server_id')
    timestamp = request.GET.get('timestamp')
    check = request.GET.get('check')
    enddate = request.GET.get('enddate')
    device_id = request.GET.get('device_id')
        

    response =  get_system_data_after(
        server_id=server_id, 
        timestamp=timestamp,
        check=check,
        enddate=enddate,
        timezone=request.timezone,
        device_id=device_id
    )

    return Response(response)



    