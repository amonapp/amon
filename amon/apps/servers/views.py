from amon.apps.core.views import *

from amon.apps.system.models import system_model
from amon.apps.servers.models import server_model
from amon.apps.devices.models import volumes_model
from amon.apps.processes.models import process_model
from amon.apps.plugins.models import plugin_model
from amon.apps.alerts.models import alerts_model
from amon.apps.servers.forms import ServerForm
from amon.apps.servers.utils import filter_tags
from amon.apps.api.models import api_key_model
from amon.apps.bookmarks.forms import BookMarkForm


@login_required
def all(request):
    api_key = api_key_model.get_or_create()
    all_servers = server_model.get_all(account_id=request.account_id)
    servers_data = []
    form = ServerForm()

    tags = request.GET.get('tags', "")
    bookmark_id = request.GET.get('bookmark_id')

    # now = unix_utc_now()

    if all_servers:
        for server in all_servers:

            append_server = filter_tags(server=server, tags=tags)
            active_server = False

            key = server.get('key')
            last_check = server.get('last_check', 0)
            # seconds_since_check = now - last_check


            server_dict = {
                'server': server,
                'key': key,
                'last_check': last_check
            }

            # Don't get data for non active servers, 48 hours as default 
            # Disable this check for now
            # if seconds_since_check < 172800:
            server_dict_data = {
                'system': system_model.get_check_for_timestamp(server, last_check),
                'volume_data': volumes_model.get_check_for_timestamp(server, last_check),
                'plugins': plugin_model.get_check_for_timestamp(server, last_check),
                'processes': process_model.get_check_for_timestamp(server, last_check),
            }

            server_dict.update(server_dict_data)
            active_server = True


            if append_server and active_server is not False:
                servers_data.append(server_dict)


        servers_data = sorted(servers_data, key=lambda k: k['last_check'], reverse=True)
    else:
        all_servers = False

    bookmark_form = BookMarkForm(initial={'tags': tags})

    return render_to_response('servers/view.html', {
        "all_servers": all_servers,
        "servers_data": servers_data,
        "form": form,
        "tags": tags,
        "bookmark_form": bookmark_form,
        "bookmark_id": bookmark_id,
        "api_key": api_key
    }, context_instance=RequestContext(request))


@login_required
def delete_data(request, server_id=None):
    if server_id:
        server_model.delete_data(server_id=server_id)

    return redirect(reverse('servers'))



@login_required
def delete_plugin(request, plugin_id=None, server_id=None):
    server = server_model.get_by_id(server_id)
    plugin = plugin_model.get_by_id(plugin_id)
    if server and plugin:
        plugin_model.delete(plugin=plugin, server=server)
        messages.add_message(request, messages.INFO, 'Plugin deleted')

    return redirect(reverse('edit_server', kwargs={"server_id": server_id}))


@login_required
def delete_server(request, server_id=None):
    server = server_model.get_by_id(server_id)

    if server:
        alerts_model.delete_server_alerts(server['_id'])
        server_model.delete(server['_id'])

    return redirect(reverse('servers'))


@login_required
def edit_server(request, server_id=None):

    server = server_model.get_by_id(server_id)
    plugins = plugin_model.get_for_server(server_id)
    form = ServerForm(server=server)

    if request.method == 'POST':
        form = ServerForm(request.POST, server=server)

        if form.is_valid():
            form.save()

            messages.add_message(request, messages.INFO, 'Server settings updated.')

            return redirect(reverse('servers'))

    return render_to_response('servers/edit.html', {
        "server": server,
        "plugins": plugins,
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def add_server(request):

    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            server = form.save()

            url = reverse('servers')
            redirect_to = "{0}#{1}".format(url, server['_id'])
            return redirect(redirect_to)
    else:
        form = ServerForm()


    return render_to_response("servers/add.html", {
        'form': form,
    }, context_instance=RequestContext(request))
