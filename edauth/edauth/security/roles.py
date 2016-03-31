# (c) 2014 Amplify Education, Inc. All rights reserved, subject to the license
# below.
#
# Education agencies that are members of the Smarter Balanced Assessment
# Consortium as of August 1, 2014 are granted a worldwide, non-exclusive, fully
# paid-up, royalty-free, perpetual license, to access, use, execute, reproduce,
# display, distribute, perform and create derivative works of the software
# included in the Reporting Platform, including the source code to such software.
# This license includes the right to grant sublicenses by such consortium members
# to third party vendors solely for the purpose of performing services on behalf
# of such consortium member educational agencies.

'''
Created on Feb 14, 2013

@author: dip
'''
from edauth import utils


class Roles:
    defined_permissions = {}
    # Pre-Populate a role of none
    defined_roles = utils.enum(NONE='NONE')
    default_permission = None

    @staticmethod
    def set_roles(mappings):
        '''
        Sets the roles.
        Mappings is a list of tuples of the form [(Allow, 'role_name', ('permissions'))]
        TODO:  We probably don't need to make it as an enum anymore
        '''
        Roles.acl = mappings
        roles = {}
        permissions = {}
        for mapping in mappings:
            role = mapping[1].upper()
            permission = mapping[2]
            roles[role] = role
            permissions[role] = permission
            if 'default' in permission:
                Roles.default_permission = role
        # Make sure we have a role of None
        if 'NONE' not in roles.keys():
            roles['NONE'] = 'NONE'
        Roles.defined_roles = utils.enum(**roles)
        Roles.defined_permissions = permissions

    @staticmethod
    def get_invalid_role():
        '''
        Returns the value of a role of None (empty memberOf from SAML response)
        '''
        return Roles.defined_roles.NONE

    @staticmethod
    def has_undefined_roles(roles):
        '''
        Given a list of roles, return true if there is an unknown role
        '''
        for role in roles:
            if Roles.defined_roles.reverse_mapping.get(role) is None:
                return True
        return False

    @staticmethod
    def has_permission(roles, permission):
        for role in roles:
            permissions = Roles.defined_permissions.get(role)
            if permissions and permission in permissions:
                return True
        return False

    @staticmethod
    def has_display_home_permission(roles):
        return Roles.has_permission(roles, 'display_home')

    @staticmethod
    def has_default_permission(roles):
        if not type(roles) is list:
            roles = [roles]
        return Roles.has_permission(roles, 'default')

    @staticmethod
    def get_default_permission():
        '''
        Returns the default permission defined.  There should only be one in the system
        '''
        return Roles.default_permission
