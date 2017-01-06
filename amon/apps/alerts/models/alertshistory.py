import math
from datetime import datetime, timedelta

from amon.apps.core.basemodel import BaseModel
from amon.apps.servers.models import server_model
from amon.utils.dates import unix_utc_now
from amon.apps.devices.models import volumes_model
from amon.apps.devices.models import interfaces_model
from amon.apps.healthchecks.models import health_checks_results_model, health_checks_model


class AlertHistoryModel(BaseModel):
    def __init__(self):
        super(AlertHistoryModel, self).__init__()
        self.collection = self.mongo.get_collection('alert_history')


    def set_task_id(self, trigger_id=None, task_id=None):
        task_id = self.mongo.get_object_id(task_id)
        self.collection.update({'_id': self.mongo.get_object_id(trigger_id)}, {"$set": {"task_id": task_id}})

    def mark_as_sent(self, trigger_id):
        self.collection.update({'_id': self.mongo.get_object_id(trigger_id)}, {"$set": {"sent": True}})


    def get_all_unsent(self):
        query_params = {'sent': False}

        results = self.collection.find(query_params)

        data = {
            'data': results.clone(), 
            'count': results.count()
        }
        
        return data

    def get_unsent(self, server_id=None):

        hour_ago = unix_utc_now()-3600
        
        query_params = {'sent': False, "time": {"$gte": int(hour_ago)}}
        if server_id:
            query_params['server_id'] = server_id

        results = self.collection.find(query_params)

        data = {
            'data': results.clone(), 
            'count': results.count()
        }
        
        return data

    # Used in the ajax popup in the alerts screen
    def get_notifications_list(self, alert_id=None, server=None, limit=0, skip=0):
        notifications_list = []

        server_id = None
        if server:
            server_id = server.get('_id') # Could be none 

        notifications = self.get_notifications(alert_id=alert_id, server_id=server_id, limit=limit, skip=skip)

        if notifications['count'] > 0:
            for notification in notifications['data']:
                
                notification_dict = {
                    "period_from": notification['from'],
                    "period_to": notification['time'],
                    "average_value": notification['average_value'],
                    "id": notification.get('_id')
                }


                # System notifications specific here
                server = server_model.get_by_id(notification.get('server_id'))
                if server:
                    notification_dict['server_id'] = server['_id']
                    notification_dict['server'] = server['name']
                    notification_dict['last_check'] = server.get('last_check')
                
                volume = notification.get('volume')
                if volume:
                    notification_dict['volume_data'] =  volumes_model.get_by_id(volume)

                interface = notification.get('interface')
                if interface:
                    notification_dict['interface_data'] =  interfaces_model.get_by_id(interface)
                
                health_checks_data_id = notification.get("health_checks_data_id")
                if health_checks_data_id:
                    health_check_data = health_checks_results_model.get_by_id(health_checks_data_id)

                    if type(health_check_data) is dict:
                    
                        health_check_id = health_check_data.get('check_id')
                        notification_dict['health_check'] = health_checks_model.get_by_id(health_check_id)

                        notification_dict['health_check_data'] = health_check_data

                notifications_list.append(notification_dict)

        return notifications_list


    def count_notifications(self, alert_id=None, date_after=None):
        query_params = {'alert_id': alert_id, 'notify': True}

        result = self.collection.find(query_params).count()

        return result


    def get_notifications(self, alert_id=None, server_id=None, limit=0, skip=0):
        query_params = {'alert_id': alert_id, 'notify': True,}

        if server_id:
            query_params['server_id'] = server_id

        results = self.collection.find(query_params).sort([('time', self.desc)]).limit(limit).skip(skip)

        data = {
            'data': results, 
            'count': results.count()
        }

        
        return data

    def get_last_trigger(self, alert_id=None):
        query_params = {'alert_id': alert_id, 'notify': True,}

        try:
            last_trigger = self.collection.find(query_params).sort([('time', self.desc)]).limit(1)[0]
        except:
            last_trigger = None

        return last_trigger

    def get_all(self, alert=None, server_id=None, reverse=False):
        server_id = self.mongo.get_object_id(server_id)
        query_params = {'server_id': server_id,'alert_id': alert['_id']}

        sort = self.asc if reverse == True else self.desc

        results = self.collection.find(query_params)
        data = {
            'data': results.clone().sort([('time', sort)]), 
            'count': results.clone().count()
        }
        
        return data

    def get_for_period(self, alert=None, server_id=None, date_after=None):
        server_id = self.mongo.get_object_id(server_id)
        query_params = {
            'server_id': server_id,
            'alert_id': alert['_id'], 
            'time': {'$gte' :date_after}
        }

        results = self.collection.find(query_params)
        data = {
            'data': results.clone().sort([('time', self.desc)]), 
            'count': results.clone().count()
        }
        
        return data

    

    def clear(self, alert_id=None, server_id=None):
        query_params = {}
        if alert_id:
            query_params['alert_id'] = self.mongo.get_object_id(alert_id)
        if server_id:
            query_params['server_id'] = self.mongo.get_object_id(server_id)

        if len(query_params) > 0:
            self.collection.remove(query_params)



    def save(self, alert=None, server_id=None, data=None):
        query_params = {'alert_id': alert['_id'], "notify": {'$exists': False}}
        
        # Plugins and Health check alerts
        if server_id:
            query_params['server_id'] = server_id


         # Disk alerts
        volume = data.get('volume', None)
        if volume:
            query_params['volume'] = volume 

        # Network alerts
        interface = data.get('interface', None)
        if interface:
            query_params['interface'] = interface
    
        trigger = data.get('trigger', False)
        time = data.get('time')

        if trigger == True:

            last_notification = self.collection.find_one(query_params)
            
            if last_notification == None:

                query_dict = query_params.copy()
                del query_dict['notify']
                data['value'] = [data['value'], ]
                data['from'] = data.get('time')
                                
                data.update(query_dict)
                
                self.collection.insert(data)

            else:
                # Update time
                self.collection.update({"_id": last_notification['_id']}, {"$set": {"time": time}, "$push": {"value": data['value']}})
                
        
            last_notification = self.collection.find_one(query_params)

            
            # Calculate time 
            time_difference = last_notification['time'] - last_notification['from']
            if time_difference >= alert['period']:
                

                value = last_notification['value']
                average_value = (math.fsum(value)/len(value))
                average_value = float("{0:.2f}".format(average_value))

                try:
                    average_value = (math.fsum(value)/len(value))
                    average_value = float("{0:.2f}".format(average_value))
                except:
                    average_value = None                


                expires_at = datetime.utcnow() + timedelta(days=7)
                
                # Trigger the alert
                trigger_data = {
                    'sent': False,
                    'notify': True,
                    'average_value': average_value,
                    'expires_at': expires_at
                }

                # Health check alert here, save result id for future reference
                health_checks_data_id = data.get('health_checks_data_id', False)
                if health_checks_data_id:
                    trigger_data['health_checks_data_id'] = health_checks_data_id


                self.collection.update({"_id": last_notification['_id']}, {"$set": trigger_data, "$unset": {'value': ""}})

        # Cleanup old notifications
        else: 
            self.collection.remove(query_params)

                        
        self.collection.ensure_index([('notify', self.desc)], background=True)
        self.collection.ensure_index([('sent', self.desc)], background=True)    
        self.collection.ensure_index([('time', self.desc)], background=True)
        self.collection.ensure_index([('server_id', self.desc)], background=True)
        self.collection.ensure_index([('alert_id', self.desc)], background=True)
        self.collection.ensure_index([('expires_at', 1)], expireAfterSeconds=0)


alertshistory_model = AlertHistoryModel()