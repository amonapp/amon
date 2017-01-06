import logging

from django.template.loader import render_to_string
from django.core import mail

from amon.apps.notifications.mail.models import email_model
from amon.apps.notifications.mail.mailer import Message

from amon.apps.notifications.mail.compiler import (
    compile_system_email,
    compile_system_email,
    compile_process_email,
    compile_process_email,
    compile_uptime_email,
    compile_plugin_email,
    compile_plugin_email,
    compile_notsendingdata_email,
    compile_health_check_email
)

logger = logging.getLogger(__name__)

def _send_email(subject=None, recipients_list=None, html_content=None):
    email_settings = email_model.get_email_settings()

    if email_settings:
        from_email = email_settings.get('sent_from')

        try:
            connection = mail.get_connection()
        except Exception as e:
            raise e

        if from_email:
            message_list = []
            for to in recipients_list:
                msg = Message(recipients=[to], 
                        sender=from_email,
                        html=html_content, 
                        subject=subject
                    )
                message_list.append(msg)

            connection.send_messages(message_list)
            


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