'''
Created on Feb 11, 2013

@author: dip
'''
from pyramid.security import (
    Allow,
    Everyone,
)


class RootFactory(object):
    __acl__ = [(Allow, 'group:allow', 'view')]

    def __init__(self, request):
        pass
