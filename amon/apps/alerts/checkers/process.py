class ProcessAlerts(object):

    def __init__(self):
        self.alert = {}

    def check(self, data, rule=None):
        value = rule.get("check") if rule.get('check') else rule.get('metric')
        value = value.lower()
        
        if value == 'memory':
            self.check_memory(rule, data)
        if value == 'cpu':
            self.check_cpu(rule, data)
        
        return self.alert

        
    def check_memory(self, rule, data):
        trigger = False
        
        if rule['above_below'] == 'above':
            if float(data['m']) > float(rule['metric_value']):
                trigger = True

        if rule['above_below'] == 'below':
            if float(data['m']) < float(rule['metric_value']):
                trigger = True


        self.alert = {'value': data['m'], 'alert_id': rule['_id'], 'trigger': trigger}
                


    def check_cpu(self, rule, data):
        trigger = False
        utilization = float(data['c'])
        
        if rule['above_below'] == 'above':
            if float(rule['metric_value']) < utilization:
                trigger = True

        if rule['above_below'] == 'below':
            if float(rule['metric_value']) > utilization:
                trigger = True

        self.alert = {'value': utilization, 'alert_id': rule['_id'], 'trigger': trigger}


process_alerts = ProcessAlerts()
