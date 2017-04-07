import logging

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from amon.apps.notifications.mail.compiler import (
    compile_system_email,
    compile_process_email,
    compile_uptime_email,
    compile_plugin_email,
    compile_notsendingdata_email,
    compile_health_check_email
)

logger = logging.getLogger(__name__)


def _send_email(subject=None, recipients_list=None, html_content=None):
    for to in recipients_list:

        msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


def send_test_email(emails=None):
    html_content = render_to_string('test.html')
    subject = "Amon Test Email"
    _send_email(subject=subject, recipients_list=emails, html_content=html_content)


def send_notification_email(notification=None, emails=None):
    sent = False

    rule_type = notification.alert.get('rule_type', 'system')

    if len(emails) > 0:
        compile_functions = {
            'system': compile_system_email,
            'global': compile_system_email,
            'process': compile_process_email,
            'process_global': compile_process_email,
            'uptime': compile_uptime_email,
            'plugin': compile_plugin_email,
            'plugin_global': compile_plugin_email,
            'notsendingdata': compile_notsendingdata_email,
            'health_check': compile_health_check_email
        }

        message = None
        if rule_type in compile_functions.keys():
            try:
                message = compile_functions[rule_type](notification=notification)
            except Exception as e:
                logger.exception('Can not generate {0} email notification'.format(rule_type))

        if message:
            _send_email(subject=message['subject'],
                recipients_list=emails,
                html_content=message['html_content'])
            sent = True

    return sent