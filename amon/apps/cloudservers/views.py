from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from amon.apps.cloudservers.forms import (
    AmazonForm,
    DigitalOceanForm,
    LinodeForm,
    RackspaceForm,
    GoogleForm,
    VultrForm
)
from amon.apps.cloudservers.models import cloud_credentials_model
from amon.apps.servers.models import cloud_server_model

PROVIDERS_FORMS = {
    'amazon': AmazonForm,
    'digitalocean': DigitalOceanForm,
    'rackspace': RackspaceForm,
    'linode': LinodeForm,
    'google': GoogleForm,
    'vultr': VultrForm,
}

from amon.apps.cloudservers.apicalls import sync_credentials


@login_required
def index(request):

    return render(request, 'cloudservers/view.html', {})


@login_required
def add(request, provider_id=None):
    all_for_provider = cloud_credentials_model.get_all_for_provider(provider_id=provider_id)
    provider_form = PROVIDERS_FORMS.get(provider_id, False)

    if request.method == "POST":
        form = provider_form(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            cloud_credentials_model.save(data=data, provider_id=provider_id)

            messages.add_message(request, messages.INFO, '{0} credentials updated'.format(provider_id.title()))
            return redirect(reverse('cloudservers_edit', kwargs={'provider_id': provider_id}))
    else:
        form = provider_form()

    return render(request, 'cloudservers/view.html', {
        "form": form,
        "provider_id": provider_id,
        "all_for_provider": all_for_provider,
        "add_form": True,
    })

@login_required
def edit(request, provider_id=None, credentials_id=None):
    provider_data = cloud_credentials_model.get_by_id(credentials_id)

    all_for_provider = cloud_credentials_model.get_all_for_provider(provider_id=provider_id)

    provider_form = PROVIDERS_FORMS.get(provider_id, False)

    if not provider_form:
        return redirect(reverse('cloudservers'))

    if request.method == "POST":
        form = provider_form(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            cloud_credentials_model.update(data=data, id=credentials_id, provider_id=provider_id)
            sync_credentials(credentials=provider_data)

            redirect_url = reverse('cloudservers_edit', kwargs={'provider_id': provider_id, 'credentials_id': credentials_id})
            messages.add_message(request, messages.INFO, '{0} credentials updated & Servers synced'.format(provider_id.title()))

            return redirect(redirect_url)
    else:
        form = provider_form(provider_data=provider_data)

    return render(request, 'cloudservers/view.html', {
        "form": form,
        "provider_data": provider_data,
        "provider_id": provider_id,
        "credentials_id": credentials_id,
        "all_for_provider": all_for_provider
    })



@login_required
def delete(request, credentials_id=None, provider_id=None):
    credentials = cloud_credentials_model.get_by_id(credentials_id)


    return render(request, "cloudservers/delete.html",
    {
        "credentials_id": credentials_id,
        "credentials": credentials,
        "provider_id": provider_id,
    })



@login_required
def delete_confirmed(request, credentials_id=None, provider_id=None):
    cloud_server_model.delete_servers_for_credentials(credentials_id=credentials_id)

    messages.add_message(request, messages.INFO, 'Credentials & associated cloud servers deleted.')

    cloud_credentials_model.delete(credentials_id)


    return redirect(reverse('cloudservers_add', kwargs={'provider_id': provider_id}))
