
class LineSitterModel:
    def __init__(self, **data):
        self.username = data.get("username")
        self.password = data.get("password")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")

    def json(self):
        return {
            "username": self.username,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name
        }
