from django.contrib.auth.decorators import login_required


from amon.utils.dates import ( 
    datestring_to_utc_datetime,
    datetime_to_unixtime,
)

from rest_framework.decorators import api_view
from rest_framework.response import Response


@login_required
@api_view(['GET'])
def ajax_localtime_to_unix(request):
    

    date_to_local = request.GET.get('date_to_local', None)

    utc_datetime = datestring_to_utc_datetime(date_to_local, tz=request.timezone)
    unixtime = datetime_to_unixtime(utc_datetime)
    

    return Response({'unixtime': unixtime})