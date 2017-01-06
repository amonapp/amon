class HealthCheckAlertChecker(object):


    def check(self, data=None, rule=None):
        self.alert = False
        exit_codes = {0: "ok", 1: "warning", 2: "critical"}
        data_command_full = data.get("command", "")

        data_command_list = data_command_full.split(" ")
        if len(data_command_list) > 0:
            data_command = data_command_list[0]
        else:
            data_command = data_command_full

        rule_command = rule.get("command").strip()
        rule_command_param = rule.get("param", "")

        rule_data_match = False

        # Global alert
        if len(rule_command_param) == 0:
            if rule_command == data_command:

                rule_data_match = True
        else:
            rule_command_param = rule_command_param.strip()
            rule_command_full = "{0} {1}".format(rule_command, rule_command_param)

            if rule_command_full == data_command_full:
                rule_data_match = True


        # Now check the conditions 
        if rule_data_match == True:
            exit_code = data.get('exit_code')
            rule_status = rule.get("status")

            try:
                current_status = exit_codes[exit_code]
            except:
                current_status = False

            if rule_status == current_status:
                self.alert = {
                    'value': current_status, 
                    'alert_id': rule['_id'], 
                    'trigger': True,
                    'health_checks_data_id': data.get('health_checks_data_id')
                }
        
         
        return self.alert


healthcheck_alert_checker = HealthCheckAlertChecker()
