#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.utils import translation
from django.template.loader import render_to_string

from amon.apps.notifications.mail.sender import _send_email


def send_email_forgotten_password(token=None, recipients=None):
    

    subject = translation.ugettext("Amon Password Reset")
    html_content = render_to_string('account/emails/reset_password.html',{
        'token': token,
    })

    _send_email(subject=subject, 
        recipients_list=recipients,
        html_content=html_content
    )


    