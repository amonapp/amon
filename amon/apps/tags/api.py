from operator import itemgetter

from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view
from rest_framework.response import Response

from amon.apps.tags.models import tags_model
from amon.apps.servers.models import server_model


def _tag_dict__repr__(tag=None):
    result = {}
    group_name = tag.get('group', {}).get('name', '')
    separator = ":" if group_name else ""
    text = "{0}{1}{2}".format(group_name, separator, tag.get('name'))

    tag_id = tag.get("_id", False)
    if tag_id:
        result = {
            'id': str(tag_id), 
            "text": text,
            'group': group_name,
        }

    return result


# AJAX 
@login_required
@api_view(['GET'])
def ajax_get_tags(request):
    all_tags = tags_model.get_all()

    q = request.GET.get('q')

    result = []
    for tag in all_tags:
        append = True
        tag_dict = _tag_dict__repr__(tag=tag)

        if q:
            append = False
            text = tag_dict.get('text', "")
            lookup = text.find(q)
            if lookup != -1:
                append = True

        if append is True:
            result.append(tag_dict)

    result = sorted(result, key=itemgetter('group')) 

    return Response(result)


# AJAX
@login_required
@api_view(['GET'])
def ajax_get_tags_list(request):
    tags = request.GET.get('tags')

    tags_list = [x.strip() for x in tags.split(',')]

    result = tags_model.get_list_of_tags(tags_list=tags_list, to_dict=True)

    return Response(result)


# AJAX 
@login_required
@api_view(['GET'])
def ajax_get_tags_for_server(request, server_id=None):
    result = []
    server = server_model.get_by_id(server_id)
    server_tags = server_model.get_tags(server=server)

    for tag in server_tags:
        tag_dict = _tag_dict__repr__(tag=tag)
        if len(tag_dict) > 0:
            result.append(tag_dict)
        
    result = sorted(result, key=itemgetter('group'))

    return Response(result)


# AJAX 
@login_required
@api_view(['GET'])
def ajax_get_only_server_tags(request):
    all_servers = server_model.get_all()

    filtered_tags = []
    for s in all_servers:
        server_tags = s.get('tags', [])
        tags_list = [x for x in server_tags]
        if len(tags_list) > 0:
            filtered_tags.extend(tags_list)

    # Filter by tag_id and leave only unique tags
    filtered_tags = dict((v['_id'], v) for v in filtered_tags).values()

    result = []
    for tag in filtered_tags:
        tag_dict = _tag_dict__repr__(tag=tag)
        if len(tag_dict) > 0:
            result.append(tag_dict)


    result = sorted(result, key=itemgetter('group'))

    return Response(result)