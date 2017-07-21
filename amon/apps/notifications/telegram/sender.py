import requests
import json


def send_telegram_notification(message=None, auth=None):
    sent = False

    token = auth.get('token')
    chat_id = auth.get('chat_id')
    bot_id = auth.get('bot_id')

    endpoint = '/sendMessage'
    url = 'https://api.telegram.org/bot' + bot_id + ':' + token + endpoint

    data = {'text': message, 'chat_id': chat_id}

    #data = json.dumps(data)
    error = None
    try:
        r = requests.get(url, params=data).json()
        print(r)
        #r = urllib.urlopen(url, urllib.urlencode(data)).read()
    except Exception as e:
        error = e

    return error