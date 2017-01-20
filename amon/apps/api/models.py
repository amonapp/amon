from amon.apps.core.basemodel import BaseModel
from datetime import datetime, timedelta
from amon.utils.dates import unix_utc_now

from amon.apps.system.models import system_model
from amon.apps.processes.models import process_model
from amon.apps.healthchecks.models import health_checks_results_model

from django.conf import settings

from amon.apps.plugins.models import plugin_model
from amon.apps.alerts.alerter import (
    server_alerter,
    process_alerter,
    uptime_alerter,
    plugin_alerter,
    health_check_alerter
)
from amon.apps.api.utils import generate_api_key


# Proxy, testable model for sending data to the backend
class ApiModel(BaseModel):

    def __init__(self):
        super(ApiModel, self).__init__()


    def save_data_to_backend(self, data=None, server=None):
        if server is None:
            return

        time_now = unix_utc_now()
        date_now = datetime.utcnow()

        expires_days = server.get('keep_data', 30)
        if settings.KEEP_DATA is not None:
            expires_days = settings.KEEP_DATA

        expires_at = date_now + timedelta(days=expires_days)

        system_data = data.get('system')
        process_data = data.get('processes')
        plugin_data = data.get('plugins')
        checks_data = data.get('checks')
        telegraf_data = data.get('series')

        if telegraf_data:
            formated_data = plugin_model.format_telegraf_to_amon(data=telegraf_data)

            if len(formated_data) > 0:
                for name, d in formated_data.items():
                    plugin = plugin_model.save_data(
                        server=server,
                        name=name,
                        data=d,
                        time=time_now,
                        expires_at=expires_at
                    )

        if system_data:
            system_model.save_data(
                server=server,
                data=system_data.copy(),
                time=time_now,
                expires_at=expires_at
            )

            server_alerter.check(data=system_data, server=server)

        if process_data:
            data = process_model.save_data(
                server=server,
                data=process_data,
                time=time_now,
                expires_at=expires_at
            )

            process_alerter.check(data=data, server=server)
            uptime_alerter.check(data=data, server=server)

        if plugin_data:
            formated_data = plugin_model.flatten_plugin_data(data=plugin_data)

            for name, data in formated_data.items():
                plugin = plugin_model.save_data(
                    server=server,
                    name=name,
                    data=data,
                    time=time_now,
                    expires_at=expires_at
                )

                plugin_alerter.check(data=data, plugin=plugin, server=server)

        if checks_data:
            formated_check_data = health_checks_results_model.save(data=checks_data, server=server)
            health_check_alerter.check(data=formated_check_data, server=server)



class ApiKeyModel(BaseModel):

    def __init__(self):
        super(ApiKeyModel, self).__init__()
        self.collection = self.mongo.get_collection('api_keys')

    def get_or_create(self):
        result = self.collection.find_one(sort=[("created", self.asc)])

        if result is None:
            self.add_initial_data()
            result = self.collection.find_one(sort=[("created", self.asc)])

        return result

    def add_initial_data(self):
        key = generate_api_key()
        data = {'label': "first-key", "key": key}

        self.add(data)

    def add(self, data=None):
        data['created'] = unix_utc_now()
        self.collection.insert(data)

        self.collection.ensure_index([('created', self.desc)], background=True)


class ApiHistoryModel(BaseModel):

    def __init__(self):
        super(ApiHistoryModel, self).__init__()
        self.collection = self.mongo.get_collection('api_history')


    def get_all(self):
        result = self.collection.find(sort=[("time", self.desc)])


        return result

    def add(self, data):
        date_now = datetime.utcnow()
        expires_at = date_now + timedelta(days=7)
        data["expires_at"] = expires_at

        self.collection.insert(data)
        self.collection.ensure_index([('time', self.desc)], background=True)
        self.collection.ensure_index([('expires_at', 1)], expireAfterSeconds=0)

api_key_model = ApiKeyModel()
api_history_model = ApiHistoryModel()
api_model = ApiModel()
