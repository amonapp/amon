import unittest
from nose.tools import eq_

from amon.apps.alerts.models import AlertHistoryModel


class AlertsHistoryModelTest(unittest.TestCase):

    def setUp(self):
        self.model = AlertHistoryModel()
        self.collection = self.model.mongo.get_collection('alert_history')
        self.server_collection = self.model.mongo.get_collection('servers')
        self.alerts_collection = self.model.mongo.get_collection('alerts')


        self.server_collection.insert({"name" : "test", "key": "test_me"})
        self.server = self.server_collection.find_one()
        server_id = str(self.server['_id'])

        rule = {"server": server_id, "rule_type": 'system', 'metric': 2}
        self.alerts_collection.insert(rule)

        self.rule = self.alerts_collection.find_one()



    def get_all_test(self):
        self.collection.remove()


        self.collection.insert({'server_id': self.server['_id'], 
            'alert_id': self.rule['_id'],
            'time':1})
        
        results = self.model.get_all(alert=self.rule, server_id=self.server['_id'])
    
        eq_(results['count'], 1)
        eq_(results['data'].count(True), 1)

        self.collection.insert({'server_id': self.server['_id'], 
            'alert_id': self.rule['_id'],
            'time':2})

        self.collection.insert({'server_id': self.server['_id'], 
            'alert_id': self.rule['_id'],
            'time':3})

        results = self.model.get_all(alert=self.rule, server_id=self.server['_id'])

        eq_(results['count'], 3)
        eq_(results['data'].count(True), 3)

        self.collection.remove()


    def get_for_period_test(self):
        self.collection.remove()

        for i in range(0, 100):
            self.collection.insert({'server_id': self.server['_id'], 
            'alert_id': self.rule['_id'],
            'time':i})
        
        results =self.model.get_for_period(alert=self.rule, server_id=self.server['_id'],
            date_after=50)

        eq_(results['count'], 50)
        eq_(results['data'].count(True), 50)

        self.collection.remove()


    def get_last_trigger_test(self):
        self.collection.remove()

        for i in range(0, 100):
            self.collection.insert({'server_id': self.server['_id'], 
            'alert_id': self.rule['_id'],
            'time':i}
        )

        self.collection.insert({'server_id': self.server['_id'], 
            'alert_id': self.rule['_id'],
            'time':101,
            'notify': True}

        )


        result = self.model.get_last_trigger(alert_id=self.rule['_id'])

        assert result['time'] == 101
        

        self.collection.remove()
    

    def clear_test(self):
        self.collection.remove()

        for i in range(0, 100):
            self.collection.insert({'server_id': self.server['_id'], 
            'alert_id': self.rule['_id'],
            'time':i})

        self.model.clear(alert_id=self.rule['_id'])
        results = self.collection.find().count()
        eq_(results, 0)

        for i in range(0, 100):
            self.collection.insert({'server_id': self.server['_id'], 
            'alert_id': self.rule['_id'],
            'time':i})

        self.model.clear(server_id=self.server['_id'])
        results = self.collection.find().count()
        eq_(results, 0)

        self.collection.remove()



    def tearDown(self):
        self.server_collection.remove()
        self.alerts_collection.remove()