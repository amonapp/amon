from django.http import HttpResponse
from django.template.loader import render_to_string

from django.conf import settings


def install_agent(request):
    domain_url = settings.HOST.rstrip('/')  # Remove trailing slash

    return HttpResponse(render_to_string('install/agent.sh', {
        'domain_url': domain_url,
        'hostname': settings.HOSTNAME

    }), content_type='text/plain; charset=utf-8')