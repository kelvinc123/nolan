
class LineSitterModel:
    def __init__(self, **data):
        self.email = data.get("email")
        self.password = data.get("password")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.phone = data.get("phone")

    def json(self):
        return {
            "email": self.email,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone
        }
