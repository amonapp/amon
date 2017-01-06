from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from amon.utils.haiku import generate_haiku_name
from amon.apps.api.permissions import ApiKeyPermission
from amon.apps.servers.models import server_model
from amon.apps.alerts.models import alerts_model
from amon.apps.api.mixins import SaveRequestHistoryMixin


class AlertsListView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)


    def get(self, request):

        alerts = alerts_model.get_all(account_id=settings.ACCOUNT_ID)

        alerts_json = []

        #         {
        #     "_id" : ObjectId("551e60bd1d41c88aa37b91b1"),
        #     "rule_type" : "process",
        #     "account_id" : 1,
        #     "metric_value" : 5,
        #     "process" : ObjectId("54e4823d1d41c86b22bd50ea"),
        #     "metric" : "Memory",
        #     "period" : 30,
        #     "server" : ObjectId("54ddb9781d41c8feae1a5b78"),
        #     "metric_type" : "MB",
        #     "above_below" : "above",
        #     "email_recepients" : [ 
        #         "54ddb8f91d41c8fd7e20264d"
        #     ],
        #     "notifications" : [ 
        #         "victorops"
        #     ],
        #     "webhooks" : [],
        #     "mute" : true
        # }
        for a in alerts:
            metric_type = "" if a.get('metric_type') == None else a.get('metric_type')
            alert_string = "{0} {1} {2}{3} for {4} seconds".format(a.get('metric'), 
                    a.get('above_below'),
                    a.get('metric_value'),
                    metric_type,
                    a.get('period')
            )
            alerts_json.append({
                'id': str(a.get('_id')), 
                'type': a.get('rule_type'),
                'metric': alert_string,
                'mute': a.get('mute'),
            })


        status = settings.API_RESULTS['ok']

        return Response({'status': status, 'alerts': alerts_json})



class AlertsMuteView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)



    def get(self, request, alert_id=None):
        alerts_model.mute(alert_id)

        alert = alerts_model.get_by_id(alert_id)
        muted = alert.get('mute')

        status = settings.API_RESULTS['ok']

        return Response({'status': status, 'muted': muted})


class AlertsMuteAllView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)

    def get(self, request):
        alerts = alerts_model.mute_all(mute=True)

        status = settings.API_RESULTS['ok']

        return Response({'status': status})


class AlertsUnMuteAllView(SaveRequestHistoryMixin, APIView):
    permission_classes = (ApiKeyPermission,)

    def get(self, request):
        alerts_model.mute_all(mute=False)

        status = settings.API_RESULTS['ok']

        return Response({'status': status})


