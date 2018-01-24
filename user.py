from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, payload):
        self.id = payload["data"]["email"]
        self._groups = payload["data"]["groups"]

    @property
    def groups(self):
        return self._groups


class Guest(User):

    def __init__(self):
        self.id = 'guest'
        self._groups = ['world']
