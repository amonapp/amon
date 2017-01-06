import kronos

import logging
logger = logging.getLogger(__name__)

from amon.apps.notifications.sender import send_notifications

@kronos.register('* * * * *')
def send_notifications_task():
    send_notifications()
    logger.debug('Sending notifications ...')