from amon.backends.mongodb import MongoBackend
from pymongo import DESCENDING, ASCENDING 
from hashlib import sha1
from os import getenv

class BaseModel(object):
    
    page_size = 50

    def __init__(self):
        self.mongo = MongoBackend()
        
        # Set in the test suite 
        #  os.environ['AMON_ENV'] = 'test'
        if getenv('AMON_ENV', None) == 'test':
            self.mongo.database = 'amon_test'

    def paginate(self, cursor, page=None):
        
        page = 1 if page == None else int(page)
        page = 1 if page == 0 else page
        
        rows = cursor.clone().count()
        total_pages = rows/self.page_size
        total_pages = 1 if total_pages == 0 else total_pages
        
        page = total_pages if page > total_pages else page

        skip = self.page_size * (page - 1)

        result = cursor.limit(self.page_size).skip(skip)

        pagination = {
                "pages": total_pages, 
                "current_page": page,
                "result": result 
        }
        
        return pagination

class DashboardModel(BaseModel):
    
    def __init__(self):
        super(DashboardModel, self).__init__()

    def get_last_system_check(self, active_system_checks):
        last_check = {}
        
        for check in active_system_checks:
            row = self.mongo.get_collection(check)
            # don't break the dashboard if the daemon is stopped
            try:
                last_check[check] = row.find({"last":{"$exists" : False}},limit=1).sort('time', DESCENDING)[0]
            except IndexError:
                last_check[check] = False

        return last_check

    def get_last_process_check(self, active_process_checks):
        process_check = {}

        for check in active_process_checks:
            row = self.mongo.get_collection(check)
            try:
                process_check[check] = row.find({"last":{"$exists" : False}}, limit=1).sort('time', DESCENDING)[0]
            except IndexError:
                process_check[check] = False

        return process_check



class SystemModel(BaseModel):

    def __init__(self):
        super(SystemModel, self).__init__()

    """
    Return pymongo object every active check
    Example: 
        active_checks = ['cpu'] will get everything in the collection amon_cpu, between date_from and date_to
    """
    def get_system_data(self, active_checks, date_from, date_to):
        
        checks = {}

        for check in active_checks:
            row = self.mongo.get_collection(check)
            
            try:
                checks[check] = row.find({"time": {"$gte": date_from,"$lte": date_to }}).sort('time', ASCENDING)
            except IndexError:
                checks[check] = False

        return checks

    """
    Used in the Javascript calendar - doesn't permit checks for dates before this date
    """
    def get_first_check_date(self):
        try:
            row = self.mongo.get_collection('cpu')
            start_date = row.find_one()
        except Exception, e:
            start_date = False

        start_date = start_date.get('time', 0)
        return start_date


    
class ProcessModel(BaseModel):
    
    def __init__(self):
        super(ProcessModel, self).__init__()

    def get_process_data(self, active_checks, date_from, date_to):
        
        process_data = {}
        for process in active_checks:
            row = self.mongo.get_collection(process)
            cursor = row.find({"time": {"$gte": date_from, '$lte': date_to}}).sort('time', ASCENDING) 
            
            process_data[process] = cursor

        return process_data


class ExceptionModel(BaseModel):
    
    def __init__(self):
        super(ExceptionModel, self).__init__()
        self.collection = self.mongo.get_collection('exceptions') 

    def get_exceptions(self):
        exceptions = self.collection.find().sort('last_occurrence', DESCENDING)

        return exceptions

    def delete_all(self):
        self.collection.remove()

class LogModel(BaseModel):
    
    def __init__(self):
        super(LogModel, self).__init__()
        self.collection = self.mongo.get_collection('logs') 
        self.tags = self.mongo.get_collection('tags')

    def get_logs(self, tags=None, search=None, page=None):
        params = {}
        
        if tags:
            tags_params = [{'tags': x} for x in tags]
            params = {"$or" : tags_params}

        if search:
            params['_searchable'] = { "$regex": str(search), "$options": 'i'}

        query = self.collection.find(params).sort('time', DESCENDING)

        logs = self.paginate(query, page)

        return logs

        
    def get_tags(self):
    
        return self.tags.find()

    def delete_all(self):
        self.collection.remove()


class UnreadModel(BaseModel):

    def __init__(self):
        super(UnreadModel, self).__init__()
        self.collection = self.mongo.get_collection('unread')

    def mark_logs_as_read(self):
        self.collection.update({"id": 1}, {"$set": {"logs": 0}})

    def mark_exceptions_as_read(self):
        self.collection.update({"id": 1}, {"$set": {"exceptions": 0}})

    def get_unread_values(self):

        record_exists = self.collection.count()

        if record_exists == 0:
            self.collection.insert({'id':1, 'exceptions': 0, 'logs': 0})

        unread_values = self.collection.find_one()
        
        return unread_values


class UserModel(BaseModel):
    
    def __init__(self):
        super(UserModel, self).__init__()
        self.collection = self.mongo.get_collection('users')


    def create_user(self, userdata):
        userdata['password'] = sha1(userdata['password']).hexdigest()
        self.collection.save(userdata)

    def check_user(self, userdata):
        userdata['password'] = sha1(userdata['password']).hexdigest()
        result = self.collection.find_one({"username": userdata['username'],
                                    "password": userdata['password']})


        return result if result else {}

    
    def count_users(self):
         return self.collection.count() 

    def username_exists(self, username):
        result = self.collection.find({"username": username}).count()

        return result


dashboard_model = DashboardModel()
process_model = ProcessModel()
system_model = SystemModel()
exception_model = ExceptionModel()
log_model = LogModel()
user_model = UserModel()
unread_model = UnreadModel()
