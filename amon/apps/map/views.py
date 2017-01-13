from amon.apps.core.views import *

from amon.apps.servers.models import server_model
from amon.apps.map.models import map_model
from amon.apps.tags.models import tag_groups_model



@login_required
def index(request):
    all_sort_fields = map_model.get_fields()
    all_servers = server_model.get_all()
    tag_groups = tag_groups_model.get_all()
    servers_data = []

    GET_group_id = request.GET.get('group_id', False)
    sort_by = request.GET.get('sort_by', 'system:cpu.system')
    
    servers_data = map_model.sort_by(field=sort_by)

    grouped_servers = []
    if GET_group_id:
        grouped_servers = map_model.group_by(group_id=GET_group_id, data=servers_data)
    
    active_tag_groups = set([])
    if all_servers:
        for server in all_servers:
            server_tags = server.get('tags', [])
            for t in server_tags:
                group_id = t.get('group_id', False)
                if group_id is not False:
                    active_tag_groups.add(str(group_id))


    return render_to_response('map/view.html', {
        "all_sort_fields": all_sort_fields,
        "grouped_servers": grouped_servers,
        "servers_data": servers_data,
        "group_id": GET_group_id,
        "sort_by": sort_by,
        "tag_groups": tag_groups,
        "active_tag_groups": active_tag_groups,
        # "group": group
    }, context_instance=RequestContext(request))
