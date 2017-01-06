from django.template.loader import render_to_string
from amon.apps.notifications.mail.sender import _send_email

def send_test_email(to_address=None):

    recipients_list = [
        to_address
    ]


    html_content = render_to_string('notifications/_alerts/emails/test.html', {})

    _send_email(recipients_list=recipients_list, 
        html_content=html_content,
        subject='Amon - Test Email'
    )
