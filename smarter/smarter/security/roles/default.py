'''
Created on May 9, 2013

@author: dip
'''
from smarter.security.roles.base import BaseRole
from smarter.security.context_role_map import ContextRoleMap


@ContextRoleMap.register(["default"])
class DefaultRole(BaseRole):
    '''
    Default role is used when a role doesn't have custom context security rule
    '''

    def __init__(self, connector, name):
        super().__init__(connector, name)

    def check_context(self, tenant, user, student_ids):
        '''
        Has Context to resource
        '''
        return True

    def add_context(self, tenant, user, query):
        '''
        noop
        '''
        pass
