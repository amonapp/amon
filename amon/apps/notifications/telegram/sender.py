import requests


def send_telegram_notification(message=None, auth=None):
    token = auth.get('token')
    chat_id = auth.get('chat_id')

    endpoint = '/sendMessage'
    url = 'https://api.telegram.org/bot' + token + endpoint

    data = {'text': message, 'chat_id': chat_id}

    error = None
    try:
        r = requests.get(url, params=data).json()
    except Exception as e:
        error = e

    return error