from django.contrib import admin

from django.shortcuts import render_to_response
from django.template import RequestContext
from amon.apps.servers.models import server_model

def servers(request, *args, **kwargs):
    
    account_id = kwargs['account_id']
    

    all_servers = server_model.get_all(account_id=int(account_id))

    return render_to_response('admin/servers.html', {
        'all_servers': all_servers,
        'title': 'Servers'
    },
    context_instance=RequestContext(request))        




admin.site.register_view('servers/(?P<account_id>\d+)', view=servers)