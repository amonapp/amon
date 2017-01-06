from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.conf import settings

from amon.apps.settings.forms import SMTPForm, DataRetentionForm, ApiKeyForm, TestSMTPForm
from amon.apps.notifications.mail.models import email_model
from amon.apps.api.models import api_key_model, api_history_model

@login_required
def data(request):

    if request.method == 'POST':
        form = DataRetentionForm(request.POST)
        if form.is_valid():
            form.save()

            messages.add_message(request, messages.INFO, 'Data Retention settings updated')
            redirect_url = reverse('settings_data')

            return redirect(redirect_url)
    else:
        form = DataRetentionForm()
    
    return render_to_response('settings/data.html', {
        "form": form
    },
    context_instance=RequestContext(request))


@login_required
def email_test(request):
        
    if request.method == 'POST':
        form = TestSMTPForm(request.POST)
        if form.is_valid():

            message = False
            
            try:
                form.save()
            except Exception as e:
                message = e

            if not message:
                send_to = form.cleaned_data['send_to']
                message  = 'Sending test email to {0}'.format(send_to)


            messages.add_message(request, messages.INFO, message)    
            redirect_url = reverse('settings_email_test')

            return redirect(redirect_url)
    else:
        form = TestSMTPForm()
    
    return render_to_response('settings/email_test.html', {
        "form": form
    },
    context_instance=RequestContext(request))




@login_required
def email(request):


    if request.method == 'POST':
        form = SMTPForm(request.POST)
        if form.is_valid():
            form.save()

            messages.add_message(request, messages.INFO, 'Email Settings saved')
            redirect_url = reverse('settings_email')

            if 'test' in request.POST:
                redirect_url = reverse('settings_email_test')
                

            return redirect(redirect_url)
    else:
        form = SMTPForm()
    
    return render_to_response('settings/email.html', {
        "form": form,
        "smtp_settings": settings.SMTP

    },
    context_instance=RequestContext(request))



@login_required
def api(request):
    api_keys = api_key_model.get_all()

    if request.method == 'POST':
        form = ApiKeyForm(request.POST)
        if form.is_valid():
            form.save()

            messages.add_message(request, messages.INFO, 'API key created')
            redirect_url = reverse('settings_api')

            return redirect(redirect_url)
    else:
        form = ApiKeyForm()
    
    return render_to_response('settings/api.html', {
        "form": form,
        "api_keys": api_keys
    },
    context_instance=RequestContext(request))


@login_required
def api_history(request):
    

    result = api_history_model.get_all()
    
    return render_to_response('settings/api_history.html', {
        "api_history": result
    },
    context_instance=RequestContext(request))


@login_required
def delete_api_key(request, key_id=None):
    
    api_key_model.delete(key_id)
    
    return redirect(reverse('settings_api'))