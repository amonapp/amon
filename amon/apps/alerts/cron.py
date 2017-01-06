import kronos
import logging

logger = logging.getLogger(__name__)
from amon.apps.alerts.alerter import notsendingdata_alerter

@kronos.register('* * * * *')
def check_not_sending_data_task():
    notsendingdata_alerter.check()    
    logger.debug('Checking for servers that do not send data ...')