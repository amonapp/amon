from amonone.web.apps.core.basemodel import BaseModel

class SystemModel(BaseModel):

    def get_system_data(self, charts, date_from, date_to):

        collection = self.mongo.get_collection('system')

        data_dict = collection.find({"time": {"$gte": date_from,"$lte": date_to }}).sort('time', self.asc)

        filtered_data = {'memory': [], "cpu": [], "disk": [], "network": [], "loadavg": []}

        # Get data for all charts
        if len(charts) == 0:
            charts = filtered_data.keys()

        for line in data_dict:
            time = line['time']

            for element in filtered_data:
                if element in charts:
                    line[element]["time"] = time
                    filtered_data[element].append(line[element])
        
        return filtered_data 


    """
    Used in the Javascript calendar - doesn't permit checks for dates before this date
    Also used to display no data message in the system tab
    """
    def get_first_check_date(self, server=None):
        
        collection = self.mongo.get_collection('system')

        start_date = collection.find_one()

        if start_date is not None:
            start_date = start_date.get('time', 0)
        else:
            start_date = 0
        
        return start_date

system_model = SystemModel()