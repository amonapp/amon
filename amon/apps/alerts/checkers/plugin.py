class PluginAlerts(object):

    def __init__(self):
        self.alert = {}


    def check_value(self, rule=None, incoming_value=None):
        trigger = False

        if rule['above_below'] == 'above':
            if float(incoming_value) > float(rule['metric_value']):
                trigger = True

        if rule['above_below'] == 'below':
            if float(incoming_value) < float(rule['metric_value']):
                trigger = True

        return trigger


    def check(self, data=None, rule=None):
        trigger = False
        gauge_data = rule.get("gauge_data")
        key = rule.get('key')
        rule_type = rule.get('rule_type', 'plugin')

        if type(gauge_data) is dict and key and rule_type == 'plugin':

            gauge_name = gauge_data.get('name')

            key_name = u"{0}.{1}".format(gauge_name, key)
            incoming_value = data.get(key_name)
            if incoming_value:
                trigger = self.check_value(rule=rule, incoming_value=incoming_value)
                self.alert = {'value': incoming_value, 'alert_id': rule['_id'], 'trigger': trigger}

        if rule_type == 'plugin_global':
            key_name = u"{0}.{1}".format(rule.get('gauge'), rule.get('key'))
            incoming_value = data.get(key_name)
            
            if incoming_value:
                trigger = self.check_value(rule=rule, incoming_value=incoming_value)
                self.alert = {'value': incoming_value, 'alert_id': rule['_id'], 'trigger': trigger}
    

        return self.alert    

plugin_alerts = PluginAlerts()
