def filter_tags(server=None, tags=None):
    show_server = False
        
    if len(tags) > 0:
        tags_list = tags.split(',')
        server_tags = server.get('tags')
        server_tag_ids = []
        for x in server_tags:
            server_tag_ids.append(str(x.get('_id')))

        # print(server_tag_ids)
        print(tags_list)
        if set(tags_list) <= set(server_tag_ids):
            print("boom")
            show_server = True

    else:
        show_server = True
    
    return show_server

    
            
    

    