
class RequestModel:
    def __init__(self, user_id, address, latitude, longitude, zip_code, price, wait_time=None, place_type=None, types=None, details=None, line_sitter=None, all_line_sitters=None, formatted_address=None):
        self.user_id = user_id
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.zip_code = zip_code
        self.price = price
        self.wait_time = wait_time
        self.place_type = place_type
        self.types = types
        self.details = details
        self.line_sitter = line_sitter
        self.all_line_sitters = all_line_sitters
        self.formatted_address = formatted_address

    def json(self):
        return {
            "user_id": self.user_id,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "zip_code": self.zip_code,
            "price": self.price,
            "wait_time": self.wait_time,
            "types": self.types,
            "place_type": self.place_type,
            "details": self.details,
            "line_sitter": self.line_sitter,
            "all_line_sitters": self.all_line_sitters,
            "formatted_address": self.formatted_address
        }