import jwt

from flask import request, current_app
from flask_login import login_user
from user import User, Guest
from eve.auth import BasicAuth


class JWTAuth(BasicAuth):

    def check_auth(self, headers):
        api_key = headers.get('X-Authorisation')

        if api_key:
            try:
                payload = jwt.decode(api_key, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            except jwt.DecodeError:
                return False
            return login_user(User(payload))

        return login_user(Guest())

    def authorized(self, allowed_roles, resource, method):
        return self.check_auth(request.headers)
