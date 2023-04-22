from service.maps import Maps

class Queueing:

    def __init__(self, mongo):
        self.mongo = mongo
        self.maps = Maps()
        self.offside = 10

    def _get_estimated_location_waiting_time(self, location):
        result = self.mongo.db.wait_times.find_one({"name": location})
        return result["wait_time"]
    
    def get_waiting_time(self, origin, destination):
        '''
        Get total waiting time for customer: time line sitter to dest + wait in line time
        '''
        time_to_dest = self.maps.get_time_to_destination(origin=origin, destination=destination)
        waiting_time = self._get_estimated_location_waiting_time(location=destination)

        return (time_to_dest["value"] / 60) + waiting_time + self.offside

    

