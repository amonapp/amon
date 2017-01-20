def filter_tags(server=None, tags=None):
    """
    >>> filter_tags(server={'name': 'frosty-mountain-6164', 'tags': ['58824ea91d41c8ed3761d8b0']}, tags='58824ea91d41c8ed3761d8b0')
    True
    >>> filter_tags(server={'name': 'frosty-mountain-6164', 'tags': ['58824761d8b0']}, tags='58824ea91d41c8ed3761d8b0')
    False
    """
    show_server = False
        
    if len(tags) > 0:
        tags_list = tags.split(',')
        server_tags = server.get('tags')  # Convert <filter object to list>
        server_tag_ids = []
        for x in server_tags:
            if type(x)is dict:
                value = str(x.get("_id"))
            else:
                value = str(x)
            server_tag_ids.append(value)

        if list(tags_list) <= list(server_tag_ids):
            show_server = True

    else:
        show_server = True
   
    return show_server