import time

from django.contrib.auth.backends import ModelBackend
from eolicowebsite.utils import connectToDb, disconnectDb
from hashlib import sha1

class AuthenticationBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            hashPassword = sha1(bytes(password, 'utf-8')).hexdigest()
            selectQuery = f"""SELECT user_id, login_email AS email, full_name, username FROM user_accounts WHERE username = '{username}' AND login_password = '{hashPassword}'"""
            connList = connectToDb()
            connList[1].execute(selectQuery)
            user = connList[1].fetchone()
            disconnectDb(connList)
            if user:
                return user
            else:
                return None
        except Exception as e:
            print(e)

    def login(self, request, user):
        request.session['user'] = user

    def logout(self, request):
        request.session['user'] = None
