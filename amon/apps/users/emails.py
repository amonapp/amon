from django.template.loader import render_to_string

from amon.apps.notifications.mail.sender import _send_email
from django.conf import settings

def send_invitation_email(invite):
    if invite:
        
        recipients_list = [invite['email']]
        subject = 'You have been invited to join Amon.'
        
        html_content = render_to_string('users/emails/invite.html', {
            'invite': invite,
            "domain_url": settings.HOST
        })


        _send_email(subject=subject, 
        recipients_list=recipients_list, 
        html_content=html_content)
    


def send_revoked_email(user=None):
    if user:
        
        email = user['email']

        subject = 'Your access to {0} has been revoked.'.format(settings.HOST)
        
        html_content = render_to_string('users/emails/revoked.html', {
            'user': user,
            "domain_url": settings.HOST
        })

        _send_email(subject=subject, 
        recipients_list=[email], 
        html_content=html_content)