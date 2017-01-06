def filter_tags(server=None, tags=None):
    show_server = False
    
    if len(tags) > 0:
        tags_list = tags.split(',')
        server_tags = server.get('tags')

        server_tag_ids = [unicode(x.get('_id')) for x in server_tags]

        if set(tags_list) <= set(server_tag_ids):
            show_server = True

    else:
        show_server = True
    
    return show_server

    
            
    

    