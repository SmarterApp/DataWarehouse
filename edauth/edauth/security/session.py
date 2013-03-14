'''
Created on Feb 15, 2013

@author: tosako
'''
import json
from edauth.security.user import User


class Session:
    def __init__(self):
        self.__initialize_session()
        # leave datetime only this class, not save in session context
        self.__expiration = None
        self.__last_access = None

    # initialize all session values
    def __initialize_session(self):
        self.__session = {}
        self.__user = User()
        self.__session_id = None
        self.__session['idpSessionIndex'] = None
        self.__session['nameId'] = None

    # serialize to text
    def get_session_json_context(self):
        # Get User Info and combined the dictionary
        combined_context = self.__user.get_user_context()
        combined_context.update(self.__session)
        return json.dumps(combined_context)

    def get_session_id(self):
        return self.__session_id

    def get_uid(self):
        return self.__user.get_uid()

    def get_roles(self):
        return self.__user.get_roles()

    def get_name(self):
        return self.__user.get_name()

    def get_idp_session_index(self):
        return self.__session['idpSessionIndex']

    def get_name_id(self):
        return self.__session['nameId']

    def get_last_access(self):
        return self.__last_access

    def get_expiration(self):
        return self.__expiration

    def get_user(self):
        return self.__user

    def set_session_id(self, session_id):
        self.__session_id = session_id

    def set_uid(self, uid):
        self.__user.set_uid(uid)

    def set_roles(self, roles):
        self.__user.set_roles(roles)

    def set_fullName(self, fullName):
        self.__user.set_full_name(fullName)

    def set_lastName(self, lastName):
        self.__user.set_last_name(lastName)

    def set_firstName(self, firstName):
        self.__user.set_first_name(firstName)

    def set_idp_session_index(self, index):
        self.__session['idpSessionIndex'] = index

    def set_name_id(self, name_id):
        self.__session['nameId'] = name_id

    def set_session(self, session):
        self.__session = session
        self.__set_user(session)

    def set_expiration(self, datetime):
        self.__expiration = datetime

    def set_last_access(self, datetime):
        self.__last_access = datetime

    def __set_user(self, info):
        self.__user.set_user_info(info)
