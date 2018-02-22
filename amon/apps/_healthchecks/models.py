import hashlib

from amon.apps.core.basemodel import BaseModel
from amon.utils.dates import unix_utc_now
from amon.utils import AmonStruct
from operator import itemgetter
from amon.apps.servers.models import server_model


from datetime import datetime, timedelta

class HealthChecksResultsModel(BaseModel):

        def __init__(self):
            super(HealthChecksResultsModel, self).__init__()
            self.collection = self.mongo.get_collection("health_checks_data")


        def save(self, data=None, server=None):
            now = unix_utc_now()

            date_now = datetime.utcnow()
            expires_at = date_now + timedelta(days=2)

            for i, check in enumerate(data):
                command = check.get('command')
                
                check_id = health_checks_model.save(
                    server=server,
                    command=command
                )

                check_id = self.object_id(check_id)

                exit_codes = {0: "ok", 1: "warning", 2: "critical"}
                try:
                    status = exit_codes[check["exit_code"]]
                except:
                    status = "unknown"

                error = check.get('error')

                output = check.get('output', "").strip()

                params = {
                    'check_id': check_id,
                    'time': now,
                    'output': output,
                    'status': status,
                    'error': error,
                    'expires_at': expires_at,
                }
                
                health_checks_data_id = self.collection.insert(params)
                self.collection.ensure_index([('expires_at', 1)], expireAfterSeconds=0)
                self.collection.ensure_index([('time', self.desc)])
                self.collection.ensure_index([('check_id', self.desc)])

                last_check = {
                    'time': now,
                    'output': output,
                    'status': status,
                    'error': error

                }

                health_checks_model.save_last_result(check_id=check_id, last_check=last_check, timestamp=now)

                data[i]['health_checks_data_id'] = health_checks_data_id

            return data





class HealthChecksModel(BaseModel):


    def __init__(self):
        super(HealthChecksModel, self).__init__()
        self.collection = self.mongo.get_collection('health_checks')
        self.data_collection = self.mongo.get_collection("health_checks_data")

    def save_last_result(self, check_id=None, last_check=None, timestamp=None):
        self.collection.update({"_id": check_id}, {"$set": {"last_check": last_check, "time": timestamp}})


    def save(self, command=None, server=None):
        command_unique_id = hashlib.md5(command.encode()).hexdigest()
        command_split =  command.split(" ")

        if len(command_split) > 1:
            command_params = " ".join(command_split[1:])
            command_string = command_split[0]
        else:
            command_params = False
            command_string = command_split[0]

        params = {'unique_id': command_unique_id, 'server_id': server['_id']}

        result = self.collection.find_one(params)
        if result is None:
            data = {
                'unique_id': command_unique_id, 
                'server_id': server['_id'],
                "command": command_string,
                'params': command_params
            }
            check_id = self.collection.insert(data)

            self.collection.ensure_index([('unique_id', self.desc)])
            self.collection.ensure_index([('params', self.desc)])
            self.collection.ensure_index([('command', self.desc)])
            self.collection.ensure_index([('server_id', self.desc)])

        else:
            check_id = result.get('_id')

        return check_id


    def sort_and_filter(self, sort_by=None, filter_by=None):
        flat_list = []
        sorted_result = []
        all_checks = []
        all_servers = server_model.get_all()

        for check in self.get_all():
            last_check = check.get('last_check')

            try:
                server = server_model.get_by_id(check['server_id'])
            except:
                server = None

            check['server'] = server

            # Append result only for existing servers
            if server != None:
                flat_list.append(check)

            if sort_by is None and filter_by is None:
                if server != None:
                    all_checks.append(check)

        sort_priority = {'critical': 1, 'warning': 2, 'ok': 3, 'unknown': 4}
        count_statuses = {'critical': 0, 'warning': 0, 'ok': 0, 'unknown': 0}

        for r in flat_list:
            result = r.get("last_check", {})
            
            if result:
                check_status = result.get('status')
                try:
                    count_statuses[check_status] = count_statuses[check_status] + 1
                except:
                    pass


        if filter_by:
            reodered_list = []
            for el in flat_list:
                check_status = el.get('last_check', {}).get('status')
                if check_status == filter_by:
                    reodered_list.append(el)

            sorted_result = sorted(reodered_list, key=lambda d: d.get('last_check', {}).get('status'))

    
        if sort_by:
            # ?sort_by=host&filter_by=critical
            if filter_by:
                flat_list = sorted_result

            if sort_by == 'status':
                reodered_list = []
                for el in flat_list:
                    try:
                        el['priority'] = sort_priority.get(el.get('last_check', {}).get('status'))
                    except:
                        pass

                    reodered_list.append(el)

                sorted_result = sorted(reodered_list, key=itemgetter('priority'))

            elif sort_by == 'host':
                sorted_result = sorted(flat_list, key=lambda d: d.get('server', {}).get('name'))

        result = AmonStruct()
        result.all_checks = all_checks
        result.sorted_result = sorted_result
        result.count_statuses = count_statuses
        result.flat_list = flat_list

        return result

    def delete(self, check_id=None):
        check_id = self.object_id(check_id)
        self.collection.remove(check_id)


class HealthChecksAPIModel(BaseModel):
    def __init__(self):
        super(HealthChecksAPIModel, self).__init__()
        self.collection = self.mongo.get_collection('health_checks')

    def get_commands_for_server(self, server_id=None):
        server_id = self.object_id(server_id)
        result = self.collection.find({'server_id': server_id})

        return result


    def get_unique_commands(self):
        all_commands = self.collection.find()

        unique_commands_list = []
        for c in all_commands:
            command = c.get('command')
            unique_commands_list.append(command)

        result = list(set(unique_commands_list))
        
        return result

    def get_params_for_command(self, command_string=None):
        unique_params_list = []
        query = self.collection.find({'command': command_string})
        for r in query:
            params = r.get('params')
            if params != False:
                unique_params_list.append(params)

        result = list(set(unique_params_list))

        return result


health_checks_api_model = HealthChecksAPIModel()
health_checks_model = HealthChecksModel()
health_checks_results_model = HealthChecksResultsModel()
