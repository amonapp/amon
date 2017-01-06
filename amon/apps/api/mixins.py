from amon.utils.dates import unix_utc_now 
from amon.apps.api.models import api_history_model

class SaveRequestHistoryMixin(object):

    def finalize_response(self, request, response, *args, **kwargs):
        
        request_data = { 
            'remote_address': request.META['REMOTE_ADDR'],
            'request_method': request.method, 
            'request_path': request.get_full_path(), 
            'time': unix_utc_now()
        }

        api_history_model.add(request_data)
    
        return super(SaveRequestHistoryMixin, self).finalize_response(request, response, *args, **kwargs)