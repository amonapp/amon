from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from amon.apps.settings.forms import DataRetentionForm, ApiKeyForm, CleanupDataForm
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
    
    return render(request, 'settings/data.html', {
        "form": form
    })


@login_required
def cleanup(request):

    if request.method == 'POST':
        form = CleanupDataForm(request.POST)
        if form.is_valid():
            form.save()

            messages.add_message(request, messages.INFO, 'Cleaning up')
            redirect_url = reverse('settings_cleanup')

            return redirect(redirect_url)
    else:
        form = CleanupDataForm()
    
    return render(request, 'settings/cleanup.html', {
        "form": form
    })


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
    
    return render(request, 'settings/api.html', {
        "form": form,
        "api_keys": api_keys
    })


@login_required
def api_history(request):
    

    result = api_history_model.get_all()
    
    return render(request, 'settings/api_history.html', {
        "api_history": result
    })


@login_required
def delete_api_key(request, key_id=None):
    
    api_key_model.delete(key_id)
    
    return redirect(reverse('settings_api'))