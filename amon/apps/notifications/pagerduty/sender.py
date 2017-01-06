import requests
import json


def send_pagerduty_notification(message=None, auth=None):
    sent = False
    url = "https://events.pagerduty.com/generic/2010-04-15/create_event.json"

    incident_key = auth.get('incident_key', 'amon')
    
    # {    
    #      "service_key": "servicekey",
    #      "incident_key": "disk/local",
    #      "event_type": "trigger",
    #      "description": "Disk > 80% for 15 minutes",
    #      "client": "local",
    #      "details": {
    #        "average_value": 63
    #     }
    # }

    data = {'service_key': auth.get('api_key'),
            'incident_key': incident_key,
            'event_type': 'trigger',
            'description': message
            }

    data = json.dumps(data)
    error = None
    
    try:
        r = requests.post(url, data=data, timeout=5)
    except Exception as e:
        error = e

    return error