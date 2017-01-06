from django.http import HttpResponse
from django.template.loader import render_to_string

from django.conf import settings


def install_agent(request):

    master_port = settings.REMOTE_PORT if settings.REMOTE_PORT else 4506
    master_ip = settings.REMOTE_IP if settings.REMOTE_IP else settings.HOSTNAME
    domain_url = settings.HOST.rstrip('/') # Remove trailing slash

    return HttpResponse(render_to_string('install/agent.sh',{
        'domain_url': domain_url,
        'master_port': master_port,
        "master_ip": master_ip,
        'hostname': settings.HOSTNAME

    }), 
    content_type='text/plain; charset=utf-8')


def install_agent_legacy(request):

    master_port = settings.REMOTE_PORT if settings.REMOTE_PORT else 4506
    master_ip = settings.REMOTE_IP if settings.REMOTE_IP else settings.HOSTNAME
    domain_url = settings.HOST.rstrip('/') # Remove trailing slash

    return HttpResponse(render_to_string('install/agent-legacy.sh',{
        'domain_url': domain_url,
        'master_port': master_port,
        "master_ip": master_ip,
        'hostname': settings.HOSTNAME

    }), 
    content_type='text/plain; charset=utf-8')


def agent_config(request, server_key):
    return HttpResponse(render_to_string('install/agent.conf',{
        'server_key': server_key,
        'domain_url': settings.HOST,
    }), 
    content_type='text/plain; charset=utf-8')