from django.contrib import admin

from django.shortcuts import render
from amon.apps.servers.models import server_model


def servers(request, *args, **kwargs):
    
    account_id = kwargs['account_id']
    

    all_servers = server_model.get_all(account_id=int(account_id))

    return render(request, 'admin/servers.html', {
        'all_servers': all_servers,
        'title': 'Servers'
    })        




admin.site.register_view('servers/(?P<account_id>\d+)', view=servers)