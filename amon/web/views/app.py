from datetime import timedelta
from tornado.web import authenticated
from amon.core import settings
from amon.web.views.base import BaseView
from amon.utils.dates import (
        datestring_to_utc_datetime,
        datetime_to_unixtime,
        utc_unixtime_to_localtime,
        localtime_utc_timedelta,
        utc_now_to_localtime
        )
from amon.system.utils import get_disk_volumes, get_network_interfaces
from amon.web.models import (
        dashboard_model,        
        system_model,
        process_model,
        exception_model,
        log_model,
        unread_model
        )

class DashboardView(BaseView):

    def initialize(self):
        super(DashboardView, self).initialize()

    @authenticated
    def get(self):

        active_process_checks = settings.PROCESS_CHECKS
        active_system_checks = settings.SYSTEM_CHECKS

        # Get the first element from the settings - used for the last check date in the template
        try:
            process_check_first = active_process_checks[0]
        except IndexError:
            process_check_first = False

        try:
            system_check_first = active_system_checks[0]
        except IndexError: 
            system_check_first = False

        last_system_check = dashboard_model.get_last_system_check(active_system_checks)
        last_process_check = dashboard_model.get_last_process_check(active_process_checks)

        self.render("dashboard.html",
                current_page='dashboard',
                last_check=last_system_check,
                process_check=last_process_check,
                system_check_first=system_check_first,
                process_check_first=process_check_first,
                )

class SystemView(BaseView):

    def initialize(self):
        super(SystemView, self).initialize()

    @authenticated
    def get(self):
        date_from = self.get_argument('date_from', False)
        date_to = self.get_argument('date_to', False)
        charts = self.get_arguments('charts', None)

        if date_from:
            date_from = datestring_to_utc_datetime(date_from)
        # Default - 24 hours period
        else:
            day = timedelta(hours=24)
            date_from = self.now - day

        if date_to:
            date_to = datestring_to_utc_datetime(date_to)
        else:
            date_to = self.now

        date_from = datetime_to_unixtime(date_from)
        date_to = datetime_to_unixtime(date_to)

        if len(charts) > 0:
            active_checks = charts
        else:
            active_checks = settings.SYSTEM_CHECKS

        checks = system_model.get_system_data(active_checks, date_from, date_to)
        first_check_date = system_model.get_first_check_date()

        # Convert the dates to local time for display
        first_check_date = utc_unixtime_to_localtime(first_check_date)
        date_from = utc_unixtime_to_localtime(date_from)
        date_to = utc_unixtime_to_localtime(date_to)

        # Get the difference between UTC and localtime - used to display 
        # the ticks in the charts
        zone_difference = localtime_utc_timedelta()

        # Get the max date - utc, converted to localtime
        max_date = utc_now_to_localtime()

        if checks != False:
            network = []
            network_interfaces = []

            disk = []
            volumes = []

            # Add network adapters 
            if 'network' in active_checks:
                for check in checks['network']:
                    network.append(check)   

                _interfaces = get_network_interfaces()
                for interface in _interfaces:
                    if interface not in network_interfaces:
                        network_interfaces.append(interface)

            # Add disk volumes
            if 'disk' in active_checks:
                for check in checks['disk']:
                    disk.append(check)

                _volumes = get_disk_volumes()
                for volume in _volumes:
                    if volume not in volumes:
                        volumes.append(volume)

            self.render('system.html',
                    current_page='system',
                    active_checks=active_checks,
                    charts=charts,
                    checks=checks,
                    network=network,
                    network_interfaces=network_interfaces,
                    volumes=volumes,
                    disk=disk,
                    date_from=date_from,
                    date_to=date_to,
                    first_check_date=first_check_date,
                    zone_difference=zone_difference,
                    max_date=max_date
                    )

class ProcessesView(BaseView):

    def initialize(self):
        super(ProcessesView, self).initialize()
        self.current_page = 'processes'

    @authenticated
    def get(self):

        processes = self.get_arguments('processes', None)
        date_from = self.get_argument('date_from', False)
        date_to = self.get_argument('date_to', False)

        if date_from:
            date_from = datestring_to_utc_datetime(date_from)
        # Default - 24 hours period
        else:
            day = timedelta(hours=24)
            date_from = self.now - day

        if date_to:
            date_to = datestring_to_utc_datetime(date_to)
        else:
            date_to = self.now

        date_from = datetime_to_unixtime(date_from)
        date_to = datetime_to_unixtime(date_to)


        all_processes_checks = settings.PROCESS_CHECKS

        if len(processes) > 0:
            processes_checks = processes
        else:
            processes_checks = settings.PROCESS_CHECKS

        process_data = process_model.get_process_data(processes_checks, date_from, date_to)

        # Convert the dates to local time for display
        date_from = utc_unixtime_to_localtime(date_from)
        date_to = utc_unixtime_to_localtime(date_to)

        # Get the difference between UTC and localtime - used to display 
        # the ticks in the charts
        zone_difference = localtime_utc_timedelta()

        # Get the max date - utc, converted to localtime
        max_date = utc_now_to_localtime()

        self.render('processes.html',
                current_page=self.current_page,
                all_processes_checks=all_processes_checks,
                processes_checks=processes_checks,
                processes=processes,
                process_data=process_data,
                date_from=date_from,
                date_to=date_to,
                zone_difference=zone_difference,
                max_date=max_date
                )


class ExceptionsView(BaseView):

    def initialize(self):
        super(ExceptionsView, self).initialize()
        self.current_page = 'exceptions'

    @authenticated
    def get(self):

        exceptions = exception_model.get_exceptions()
        unread_model.mark_exceptions_as_read()

        self.render('exceptions.html',
                exceptions=exceptions,
                current_page=self.current_page,
                )

class LogsView(BaseView):

    def initialize(self):
        super(LogsView, self).initialize()
        self.current_page = 'logs'

    @authenticated
    def get(self):
        page = self.get_argument('page',1)
        tags = self.get_arguments('tags', None)
        query = self.get_argument('query', None)

        logs = log_model.get_logs(tags, query, page)
        all_tags = log_model.get_tags()
        unread_model.mark_logs_as_read()

        self.render('logs.html',
                current_page=self.current_page,
                logs=logs,
                tags=tags,
                all_tags=all_tags,
                query=query
                )

class SettingsView(BaseView):

    def initialize(self):
        super(SettingsView, self).initialize()
        self.current_page = 'settings'

    @authenticated
    def get(self, action=None):

        message = self.session.get('message', '')

        try:
            del self.session['message']
        except:
            pass

        if action != None:
            if action == 'delete_exceptions':
                exception_model.delete_all()
                self.session['message'] = 'All Exceptions deleted'
                self.redirect('/settings')

            if action == 'delete_logs':
                log_model.delete_all()
                self.session['message'] = 'All Logs deleted'
                self.redirect('/settings')
        else:
            self.render('settings.html',
                    current_page=self.current_page,
                    message=message
                    )


