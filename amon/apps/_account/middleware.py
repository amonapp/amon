from datetime import datetime
from django.conf import settings

# from amon.utils.dates import localtime_utc_timedelta
# from amon.apps.dashboards.models import dashboard_model
# from amon.apps.bookmarks.models import bookmarks_model
from amon import VERSION
from django.utils.deprecation import MiddlewareMixin

class AccountMiddleware(MiddlewareMixin):

    def process_request(self, request):

        #  Defaults
        request.now = datetime.utcnow()
        request.debug = settings.DEBUG
        request.version = VERSION

        request.timezone = 'UTC'

        if request.user.is_authenticated:
            # user_preferences = user_preferences_model.get_preferences(user_id=request.user.id)

            # user_timezone = user_preferences.get('timezone', 'UTC')
            # request.timezone = str(user_timezone)  # Pytz timezone object
            # request.timezone_offset = localtime_utc_timedelta(tz=request.timezone)

            # request.account_id = settings.ACCOUNT_ID

            # request.dashboards = dashboard_model.get_all(account_id=request.account_id)

            # request.bookmarks = bookmarks_model.get_all()

            # Enable disable minified js and css files
            try:
                request.devmode = settings.DEVMODE
            except:
                request.devmode = False


    def process_view(self, request, view_func, view_args, view_kwargs):
        request.current_page = request.resolver_match.url_name

        request.server_pages = ['server_system', 'view_process', 'add_server', 'edit_server']
