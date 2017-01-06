from operator import itemgetter

from amon.apps.core.basemodel import BaseModel

class TagsModel(BaseModel):

    def __init__(self):
        super(TagsModel, self).__init__()
        self.collection = self.mongo.get_collection('tags')

    def get_for_group(self, group_id):
        group_id = self.object_id(group_id)
        result = self.collection.find({'group_id': group_id})

        return result


    def get_list_of_tags(self, tags_list=None, to_dict=None):
        result = []
        tags = [self.object_id(x) for x in tags_list]
        

        query = self.collection.find({'_id': {"$in": tags}})

        for tag in query:
            group = tag_groups_model.get_by_id(tag.get('group_id'))
            if group:
                tag['full_name'] = "{0}.{1}".format(group.get('name', ''), tag.get('name'))

            else:
                tag['full_name'] = "{0}".format(tag.get('name'))
            
            tag['text'] = tag['full_name'] # Used for the dropdown menu
            
            if to_dict == True:
                tag = self.mongoid_to_str(tag, keys=['_id', 'group_id'])
                tag['id'] = tag['_id'] # Used in the dropdown
                
            result.append(tag)

        
        return result

    def create_and_return_ids(self, tags=None):
        tags_list = []
        
        # {'rds': 'value'}
        if type(tags) is dict:
            for group, tag in tags.items():
                group_id = tag_groups_model.get_or_create_by_name(group)
                _id = self.get_or_create(name=tag, group_id=group_id)
                tags_list.append(_id)

        # ['tag', 'onemore', 'provider:digitalocean']
        if type(tags) is list:
            for t in tags:
                # provider:digitalocean
                try:
                    group, tag = t.split(":")
                # tag
                except ValueError:
                    tag = t
                    group = False

                if group:
                    group_id = tag_groups_model.get_or_create_by_name(group)
                    _id = self.get_or_create(name=tag, group_id=group_id)

                else:
                    _id = self.get_or_create_by_name(name=tag)

                tags_list.append(_id)

        return tags_list

    def get_by_id(self, id):
        result = super(TagsModel, self).get_by_id(id)
        
        if result:
            group_id = result.get('group_id')
            if group_id:
                result['group'] = tag_groups_model.get_by_id(group_id)


        return result

    def get_all(self):
        result_list = []
        result = super(TagsModel, self).get_all()
        for r in result:
            group_id = r.get('group_id')
            if group_id:
                r['group'] = tag_groups_model.get_by_id(group_id)
            result_list.append(r)

        try:
            result_list = sorted(result_list, key=itemgetter('group'))
        except:
            pass

        return result_list

    def get_or_create(self, name=None, group_id=None):
        params = {'name': name}

        if group_id:
            group_id = self.object_id(group_id)
            params['group_id'] = group_id


        result = self.collection.find_one(params)
        if result == None:
            _id = self.collection.insert(params)
        else:
            _id = result['_id']

        self.collection.ensure_index([('name', self.desc)], background=True)

        return _id

    def get_or_create_by_name(self, name=None):
        cleanup_name = name.strip()

        # Don't create empty tags
        if len(cleanup_name) < 2:
            return 

        result = self.collection.find_one({'name': cleanup_name})
            
        if result == None:
            _id = self.collection.insert({'name': cleanup_name})
        else:
            _id = result['_id']
    

        self.collection.ensure_index([('name', self.desc)], background=True)

        return _id 


    def update(self, data, id):
        data = self.keys_to_mongoid(data, ['group_id'])
        super(TagsModel, self).update(data, id)


    def get_tags_ids(self, tags_string=None):
        tags_list = tags_string.split(',')
        
        result = []

        for t in tags_list:
            try:
                tag_id = self.get_by_id(t)['_id']
            except:
                tag_id = self.get_or_create_by_name(name=t)

            result.append(tag_id)
            

        return result


class TagGroupsModel(BaseModel):

    def __init__(self):
        super(TagGroupsModel, self).__init__()
        self.collection = self.mongo.get_collection('tag_groups')


    def get_or_create_by_name(self, name=None):
        cleanup_name = name.strip()

        # Don't create empty tags
        if len(cleanup_name) < 2:
            return 

        result = self.collection.find_one({'name': cleanup_name})
            
        if result == None:
            _id = self.collection.insert({'name': cleanup_name})
        else:
            _id = result['_id']
    

        self.collection.ensure_index([('name', self.desc)], background=True)

        return _id 


tag_groups_model = TagGroupsModel()
tags_model = TagsModel()
