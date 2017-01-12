from django.conf import settings
from datetime import datetime, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response


from amon.apps.plugins.models import plugin_model
from amon.apps.api.throttle import CheckPeriodThrottle

from amon.utils.dates import unix_utc_now


class CollectdDataView(APIView):

    throttle_classes = (CheckPeriodThrottle,)

    # Data Format 
    # {u'dstypes': [u'gauge'],
    # u'plugin': u'users', u'dsnames': [u'value'],
    #  u'interval': 10.0, u'host': u'ubuntu', u'values': [7], 
    #  u'time': 1424233591.485, u'plugin_instance': u'', 
    #  u'type_instance': u'', u'type': u'users'}
    def post(self, request, server_key):

        plugin_dict = {}
        date_now = datetime.utcnow()
        time_now = unix_utc_now()
        ignored_plugins = ['irq']
        accepted_types = ['gauge',]

        status = settings.API_RESULTS['not-found']
        
        data = request.data


        if request.server:
            server = request.server
            
            expires_days = server.get('keep_data', 30)
            expires_at = date_now + timedelta(days=expires_days)
        
            for p in data:
                
                plugin_name = p.get('plugin')
                plugin_instance = p.get('plugin_instance')
                dsnames = p.get('dsnames')
                values = p.get('values')
                dstypes = p.get('dstypes')

                name = "collectd.{0}".format(plugin_name)
                
                plugin_dict[name] = {}
                for dsn, v, dstype in zip(dsnames, values, dstypes):
                    if dstype in accepted_types and plugin_name not in ignored_plugins:
                        value_name = "{0}.{1}".format(plugin_instance, dsn) if plugin_instance else dsn
                        value_name = "{0}.{1}".format(plugin_name, value_name) if dsn == 'value' else value_name

                        plugin_dict[name][value_name] = v
                    
            if len(plugin_dict) > 0:
                for name, data in plugin_dict.iteritems():
                    
                    if len(data) > 0:
                        plugin_data = {'gauges': data, 'counters':{}}
                        
                        plugin_model.save_data(
                            server=server, 
                            name=name, 
                            data=plugin_data,
                            time=time_now,
                            expires_at=expires_at
                        )

    
        return Response({'status': status})


