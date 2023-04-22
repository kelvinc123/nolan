
class PresenceModel:
    def __init__(self, line_sitter_id, latitude, longitude, zip_code):
        self.line_sitter_id = line_sitter_id
        self.latitude = latitude
        self.longitude = longitude
        self.zip_code = zip_code

    def json(self):
        return {
            "line_sitter_id": self.line_sitter_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "zip_code": self.zip_code
        }