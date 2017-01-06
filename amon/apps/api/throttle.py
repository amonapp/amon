from rest_framework.throttling import BaseThrottle

from amon.apps.servers.models import server_model
from amon.apps.api.utils import throttle_status

class CheckPeriodThrottle(BaseThrottle):
    
    def allow_request(self, request, view):
        request.server = None
        allow = True

        view_name = view.get_view_name()

        allowed_views = [u'System Data', u'Collectd Data', u'Legacy System Data']
        
        if view_name in allowed_views:
            server_key = view.kwargs.get('server_key')
            server = server_model.get_server_by_key(server_key)

            if server:

                request.server = server # Needed in the Models
                server_status = throttle_status(server=server)

                
                if server_status.allow == False:
                    allow = False
            

        return allow
