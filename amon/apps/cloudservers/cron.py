import kronos

from amon.apps.cloudservers.apicalls import sync_credentials
from amon.apps.cloudservers.models import cloud_credentials_model

    
# */5 * * * * command
# 2015-01-03 07:05:00 UTC
# 2015-01-03 07:10:00 UTC
# 2015-01-03 07:15:00 UTC
# 2015-01-03 07:20:00 UTC
@kronos.register('*/5 * * * *')
def sync_cloudservers_task():
    credentials = cloud_credentials_model.get_all()
    for c in credentials:
        sync_credentials(credentials=c)
        