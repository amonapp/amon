import unittest
import hashlib
from datetime import datetime

from amon.apps.healthchecks.models import (
    health_checks_model, 
    health_checks_results_model, 
    health_checks_api_model
)
from amon.apps.servers.models import server_model
from amon.utils.dates import unix_utc_now



class HealthChecksResultsModelTest(unittest.TestCase):

    def setUp(self):
        server_model.collection.insert({"name": "test"})
        self.server = server_model.collection.find_one()


    def tearDown(self):
        self._cleanup()

    def _cleanup(self):
        health_checks_model.collection.remove()
        health_checks_results_model.collection.remove()
        server_model.collection.remove()

    def save_test(self):
        self._cleanup()

        data = [{u'output': u'CheckDisk WARNING: / 83.35% bytes usage (29 GiB/35 GiB)\n', u'command': u'check-disk-usage.rb -w 80 -c 90', u'exit_code': 1}]

        formated_data = health_checks_results_model.save(data=data, server=self.server)
        for d in formated_data:
            assert set(d.keys()) == set(['output', 'command', 'exit_code', 'health_checks_data_id'])

        assert health_checks_results_model.collection.find().count() == 1
        assert health_checks_model.collection.find().count() == 1

        result =  health_checks_model.collection.find_one()

        assert result['command'] == "check-disk-usage.rb"
        assert result['params'] == "-w 80 -c 90"
        assert result['unique_id'] == hashlib.md5("check-disk-usage.rb -w 80 -c 90".encode()).hexdigest()
        assert result['last_check']['status'] == 'warning'


        self._cleanup()

        for i in range(50):
            health_checks_results_model.save(data=data, server=self.server)


        assert health_checks_results_model.collection.find().count() == 50
        assert health_checks_model.collection.find().count() == 1

        result = health_checks_model.collection.find_one()



class HealthChecksModelTest(unittest.TestCase):


    def _cleanup(self):
        health_checks_model.collection.remove()
        health_checks_results_model.collection.remove()
        server_model.collection.remove()


    def test_sort_and_filter(self):
        self._cleanup()

        server_model.collection.insert({"name": "check_sort_and_filter_default"})
        server = server_model.collection.find_one()

        for i in range(0, 10):
            data = [{
                'command': "check_sort_and_filter_default.rb",
                'exit_code': 1,
                'output': 'CheckDisk WARNING: / 83.35% bytes usage (29 GiB/35 GiB)'
            }]
            health_checks_results_model.save(data=data, server=server)

        result = health_checks_model.sort_and_filter()

        assert len(result.all_checks) == 1
        assert result.all_checks[0]['last_check']
        assert result.all_checks[0]['last_check']['status'] == 'warning'

        self._cleanup()
        
    
        for i in range(0, 10):
            server_id = server_model.collection.insert({"name": "{0}_server_check_sort_and_filter_by_host".format(i)})
            server = server_model.get_by_id(server_id)

            # exit_codes = {0: "ok", 1: "warning", 2: "critical"}
            exit_code = 2 if i <= 5 else 2
            exit_code = 1 if i > 5 else exit_code

            for j in range(0, 100):
                data = [{
                    'command': '{0}_check_sort_and_filter_by_host.rb'.format(i),
                    'exit_code': exit_code,
                    'output': 'CheckBanner OK: port 22 open'
                }]
            
                health_checks_results_model.save(data=data, server=server)


        result = health_checks_model.sort_and_filter(sort_by='status')
        assert len(result.sorted_result) == 10
        for i in range(0, 10):
            status = 'critical' if i <= 5 else 'ok'
            status = 'warning' if i > 5 else status
            assert result.sorted_result[i]['last_check']['status'] == status


        result = health_checks_model.sort_and_filter(sort_by='host')
        assert len(result.sorted_result) == 10
        for i in range(0, 10):
            assert result.sorted_result[i]['server']['name'] == "{0}_server_check_sort_and_filter_by_host".format(i)


        result = health_checks_model.sort_and_filter(sort_by='host', filter_by='critical')
        assert len(result.sorted_result) == 6

        result = health_checks_model.sort_and_filter(sort_by='host', filter_by='warning')
        assert len(result.sorted_result) == 4
        



    def test_save(self):
        self._cleanup()
        server_id = server_model.collection.insert({"name": "server_check_sort_and_filter_by_host"})
        server = server_model.get_by_id(server_id)
        
        command = "testmehere"
        for i in range(0, 10):
            health_checks_model.save(command=command, server=server)

        assert health_checks_model.collection.find().count() == 1




    def tearDown(self):
        health_checks_model.collection.remove()



class HealthChecksAPIModelTest(unittest.TestCase):


    def _cleanup(self):
        health_checks_model.collection.remove()
        health_checks_results_model.collection.remove()
        server_model.collection.remove()



    def test_get_commands_for_server(self):
        self._cleanup()

        server_id = server_model.collection.insert({"name": "server_check_sort_and_filter_by_host"})
        server = server_model.get_by_id(server_id)
        
        command = "testmehere -w 10"
        for i in range(0, 10):
            health_checks_model.save(command=command, server=server)

        second_command = "testmeagain -c 10"
        for i in range(0, 5):
            health_checks_model.save(command=second_command, server=server)

        result = health_checks_api_model.get_commands_for_server(server_id=server['_id'])

        assert result.count() == 2


    def test_get_unique_commands(self):
        self._cleanup()

        server_id = server_model.collection.insert({"name": "server_check_sort_and_filter_by_host"})
        server = server_model.get_by_id(server_id)

        for i in range(0, 10):
            command = "testcommand{0} -w {0} -c {0}".format(i)
            health_checks_model.save(command=command, server=server)


        result = health_checks_api_model.get_unique_commands()

        assert len(result) == 10


    def test_get_params_for_command(self):
        self._cleanup()

        server_id = server_model.collection.insert({"name": "server_check_sort_and_filter_by_host"})
        server = server_model.get_by_id(server_id)

        for i in range(0, 10):
            command = "testcommand -w {0} -c {0}".format(i)
            health_checks_model.save(command=command, server=server)

        # Duplicate - still has to return only 10 unique params
        for i in range(0, 10):
            command = "testcommand -w {0} -c {0}".format(i)
            health_checks_model.save(command=command, server=server)


        result = health_checks_api_model.get_params_for_command(command_string="testcommand")

        assert len(result) == 10
