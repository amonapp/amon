from operator import itemgetter

from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view
from rest_framework.response import Response
import boto.ec2

# AJAX 
@login_required
@api_view(['GET'])
def ajax_get_amazon_regions(request):
    result = []

    for v in boto.ec2.regions():

        result.append({"id": v.name, "text": v.name})

    result = sorted(result, key=itemgetter('text')) 

    return Response(result)



# AJAX 
@login_required
@api_view(['GET'])
def ajax_get_rackspace_regions(request):

    result = [
        {'id': 'iad', 'text': 'Northern Virginia (IAD)' },
        {'id': 'ord', 'text': 'Chicago (ORD)' },
        {'id': 'dfw', 'text': 'Dallas (DFW)' },
        {'id': 'syd', 'text': 'Sydney(SYD)' },
        {'id': 'hkg', 'text': 'Hong Kong(HKG)' },
    ]
    
    result = sorted(result, key=itemgetter('text')) 

    return Response(result)