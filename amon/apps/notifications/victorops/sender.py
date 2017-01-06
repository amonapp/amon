import requests
import json

def send_victorops_notification(message=None, auth=None):
    sent = False


    url = auth.get('rest_endpoint')
    
    #     {
    #     "message_type":"CRITICAL",
    #     "timestamp":"1383239337",
    #     "entity_id":"disk space/db01.mycompany.com",
    #     "state_message":"the disk is really really full"
    # }

    data = {'message_type': 'CRITICAL',
            'entity_id': 'amon',
            'state_message': message
    }

    data = json.dumps(data)
    error = None
    try:
        r = requests.post(url, data=data, timeout=5)
    except Exception as e:
        error = e

    return error