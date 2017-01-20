from rest_framework import permissions

from amon.apps.api.models import api_key_model
from amon.utils.dates import unix_utc_now


class ApiKeyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        api_key = request.query_params.get('api_key')
        is_valid = False

        params = {'key': api_key}
        result = api_key_model.get_one(params=params)

        key = result.get('key', False)

        if key is not False:
            is_valid = True
            api_key_model.update({'last_used': unix_utc_now()}, result['_id'])

        if request.user.is_authenticated():
            is_valid = True

        return is_valid
