'''
Created on Mar 14, 2013

@author: dip
'''
import unittest
from edauth.security.user import User, RoleRelation, UserContext
from edauth.security.roles import Roles


class TestUser(unittest.TestCase):

    def test_empty_user(self):
        user = User()
        data = {'name': {'fullName': None, 'firstName': None, 'lastName': None}, 'uid': None, 'roles': [], 'tenant': None, 'displayHome': False, 'guid': None}

        name = user.get_name()
        self.assertEqual(name, {'name': data['name']})

        uid = user.get_uid()
        self.assertEqual(uid, data['uid'])

        context = user.get_user_context()
        self.assertEqual(context, data)

        roles = user.get_roles()
        self.assertEqual(roles, data['roles'])

        tenant = user.get_tenants()
        self.assertIsNone(tenant)

        guid = user.get_guid()
        self.assertIsNone(guid)

    def test_non_empty_user(self):
        user = User()
        data = {'name': {'fullName': 'Joe Doe', 'firstName': 'Joe', 'lastName': 'Doe'}, 'uid': 'joe.doe', 'roles': ['TEACHER'], 'stateCode': [None], 'tenant': ['dog'], 'displayHome': False, 'guid': '123'}
        user.set_name(data['name'])
        user.set_uid(data['uid'])
        user.set_roles(data['roles'])
        user.set_guid(data['guid'])
        user.set_tenants(data['tenant'])

        name = user.get_name()
        self.assertEqual(name, {'name': data['name']})

        uid = user.get_uid()
        self.assertEqual(uid, data['uid'])

        context = user.get_user_context()
        self.assertEqual(context, data)

        roles = user.get_roles()
        self.assertEqual(roles, data['roles'])

        tenant = user.get_tenants()
        self.assertEqual(tenant, data['tenant'])

        guid = user.get_guid()
        self.assertEqual(guid, data['guid'])

    def test_set_individual_names(self):
        user = User()
        data = {'name': {'fullName': 'Joe MDoe', 'firstName': 'Joe', 'lastName': 'Doe'}, 'uid': 'joe.doe', 'roles': ['TEACHER'], 'tenant': ['dog'], 'displayHome': False, 'guid': '123'}
        user.set_first_name(data['name']['firstName'])
        user.set_last_name(data['name']['lastName'])
        user.set_full_name(data['name']['fullName'])

        name = user.get_name()
        self.assertEqual(name, {'name': data['name']})

    def test_get_user_context(self):
        user = User()
        data = {'name': {'fullName': 'Joe Doe', 'firstName': 'Joe', 'lastName': 'Doe'}, 'uid': 'joe.doe', 'roles': ['TEACHER'], 'tenant': 'dog', 'guid': '123'}
        user.set_name(data['name'])
        user.set_uid(data['uid'])
        user.set_roles(data['roles'])
        user.set_guid(data['guid'])
        user.set_tenants(data['tenant'])

        context = user.get_user_context()
        self.assertEqual(context['uid'], data['uid'])
        self.assertEqual(context['name'], data['name'])
        self.assertEqual(context['roles'], data['roles'])
        self.assertEqual(context['guid'], data['guid'])
        self.assertEqual(context['tenant'], [data['tenant']])

    def test_set_user_info(self):
        user = User()
        data = {'name': {'fullName': 'Joe Doe', 'firstName': 'Joe', 'lastName': 'Doe'}, 'uid': 'joe.doe', 'junk': 'junk', 'roles': ['TEACHER'], 'tenant': 'dog', 'displayHome': False, 'guid': '123'}

        user.set_user_info(data)
        context = user.get_user_context()
        self.assertEqual(len(context), 6)
        self.assertEqual(context['name'], data['name'])
        self.assertEqual(context['uid'], data['uid'])
        self.assertEqual(context['roles'], data['roles'])
        self.assertEqual(context['guid'], data['guid'])
        self.assertEqual(context['tenant'], data['tenant'])
        self.assertEqual(context['displayHome'], data['displayHome'])

    def test_user_with_tenant_as_str(self):
        user = User()
        user.set_tenants("dog")
        tenants = user.get_tenants()
        self.assertIn("dog", tenants)
        self.assertEqual(len(tenants), 1)

    def test_display_home(self):
        Roles.set_roles([('Allow', 'CONSORTIUM_EDUCATION_ADMINISTRATOR_1', ('view', 'logout', 'display_home'))])
        user = User()
        user.set_roles(['CONSORTIUM_EDUCATION_ADMINISTRATOR_1'])
        context = user.get_user_context()
        self.assertTrue(context['displayHome'])

    def test_user_context(self):
        rel_chain = [RoleRelation('CONSORTIUM_EDUCATION_ADMINISTRATOR_1', 'CA', 'CA', '1', '2'),
                     RoleRelation('CONSORTIUM_EDUCATION_ADMINISTRATOR_1', 'CA', 'CA', '1', '3'),
                     RoleRelation('CONSORTIUM_EDUCATION_ADMINISTRATOR_2', 'NY', 'NY', '2', '4')]
        uc = UserContext(rel_chain)
        self.assertEqual(uc.get_districts('CA', 'CONSORTIUM_EDUCATION_ADMINISTRATOR_1'), {'1'}, 'Must be district 1')
        self.assertEqual(uc.get_schools('CA', 'CONSORTIUM_EDUCATION_ADMINISTRATOR_1'), {'3', '2'}, 'Must be schools {2, 3}')
        self.assertEqual(uc.get_schools('NY', 'CONSORTIUM_EDUCATION_ADMINISTRATOR_2'), {'4'}, 'Must be school {4}')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
