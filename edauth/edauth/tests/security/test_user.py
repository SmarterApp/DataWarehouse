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
Created on Mar 14, 2013

@author: dip
'''
import unittest
from edauth.security.user import User, RoleRelation, UserContext
from edauth.security.roles import Roles
import edauth
from pyramid.security import Allow
from edcore.security.tenant import set_tenant_map


class TestUser(unittest.TestCase):

    def setUp(self):
        defined_roles = [(Allow, 'PII', ('view', 'logout')),
                         (Allow, 'DEFAULT', ('view', 'logout', 'default'))]
        edauth.set_roles(defined_roles)
        set_tenant_map({'tenant1': 'NC', 'tenant2': 'CA', 'tenant3': 'WA'})

    def test_empty_user(self):
        user = User()
        data = {'name': {'fullName': None, 'firstName': None, 'lastName': None}, 'uid': None, 'roles': [], 'stateCode': [], 'tenant': [], 'displayHome': False, 'guid': None}

        name = user.get_name()
        self.assertEqual(name, {'name': data['name']})

        uid = user.get_uid()
        self.assertEqual(uid, data['uid'])

        context = user.get_user_context()
        self.assertEqual(context, data)

        roles = user.get_roles()
        self.assertEqual(roles, data['roles'])

        tenant = user.get_tenants()
        self.assertEqual(0, len(tenant))

        guid = user.get_guid()
        self.assertIsNone(guid)

    def test_non_empty_user(self):
        user = User()
        data = {'name': {'fullName': 'Joe Doe', 'firstName': 'Joe', 'lastName': 'Doe'}, 'uid': 'joe.doe', 'roles': [], 'stateCode': [None], 'tenant': None, 'displayHome': False, 'guid': '123'}
        user.set_name(data['name'])
        user.set_uid(data['uid'])
        user.set_guid(data['guid'])

        name = user.get_name()
        self.assertEqual(name, {'name': data['name']})

        uid = user.get_uid()
        self.assertEqual(uid, data['uid'])

        context = user.get_user_context()
        self.assertEqual(context['displayHome'], data['displayHome'])
        self.assertEqual(context['guid'], data['guid'])

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
        user.set_guid(data['guid'])

        context = user.get_user_context()
        self.assertEqual(context['uid'], data['uid'])
        self.assertEqual(context['name'], data['name'])
        self.assertEqual(context['guid'], data['guid'])

    def test_set_user_info(self):
        user = User()
        data = {'name': {'fullName': 'Joe Doe', 'firstName': 'Joe', 'lastName': 'Doe'}, 'uid': 'joe.doe', 'junk': 'junk', 'roles': ['TEACHER'], 'stateCode': [], 'tenant': 'dog', 'displayHome': False, 'guid': '123'}

        user.set_user_info(data)
        context = user.get_user_context()
        self.assertEqual(len(context), 7)
        self.assertEqual(context['name'], data['name'])
        self.assertEqual(context['uid'], data['uid'])
        self.assertEqual(context['guid'], data['guid'])
        self.assertEqual(context['displayHome'], data['displayHome'])

    def test_display_home(self):
        Roles.set_roles([('Allow', 'CONSORTIUM_EDUCATION_ADMINISTRATOR_1', ('view', 'logout', 'display_home'))])
        user = User()
        rel_chain = [RoleRelation('CONSORTIUM_EDUCATION_ADMINISTRATOR_1', 'CA', 'CA', '1', '2')]
        user.set_context(rel_chain)
        context = user.get_user_context()
        self.assertTrue(context['displayHome'])

    def test_user_context(self):
        rel_chain = [RoleRelation('CONSORTIUM_EDUCATION_ADMINISTRATOR_1', 'CA', 'CA', '1', '2'),
                     RoleRelation('CONSORTIUM_EDUCATION_ADMINISTRATOR_1', 'CA', 'CA', '1', '3'),
                     RoleRelation('CONSORTIUM_EDUCATION_ADMINISTRATOR_2', 'NY', 'NY', '2', '4'),
                     RoleRelation('CONSORTIUM_EDUCATION_ADMINISTRATOR_1', 'CA', 'CA', '1', None)]
        uc = UserContext(rel_chain)
        self.assertEqual(uc.get_districts('CA', 'CONSORTIUM_EDUCATION_ADMINISTRATOR_1'), {'1'}, 'Must be district 1')
        self.assertEqual(uc.get_schools('CA', 'CONSORTIUM_EDUCATION_ADMINISTRATOR_1'), {'3', '2'}, 'Must be schools {2, 3}')
        self.assertEqual(uc.get_schools('NY', 'CONSORTIUM_EDUCATION_ADMINISTRATOR_2'), {'4'}, 'Must be school {4}')

    def test_get_all_user_context(self):
        rel_chain = [RoleRelation('CONSORTIUM_EDUCATION_ADMINISTRATOR_1', 'CA', None, None, None),
                     RoleRelation('CONSORTIUM_EDUCATION_ADMINISTRATOR_1', 'CA', 'CA', '1', '3'),
                     RoleRelation('CONSORTIUM_EDUCATION_ADMINISTRATOR_2', 'CA', 'CA', None, None),
                     RoleRelation('CONSORTIUM_EDUCATION_ADMINISTRATOR_1', 'CA', 'CA', '1', None)]
        uc = UserContext(rel_chain)
        all_context = uc.get_all_context('CA', 'CONSORTIUM_EDUCATION_ADMINISTRATOR_2')
        self.assertEqual(all_context['state_code'], {'CA'})
        self.assertEqual(all_context['district_id'], set())
        self.assertEqual(all_context['school_id'], set())
        all_context = uc.get_all_context('CA', 'CONSORTIUM_EDUCATION_ADMINISTRATOR_1')
        self.assertEqual(all_context['state_code'], set())
        self.assertEqual(all_context['district_id'], {'1'})
        self.assertEqual(all_context['school_id'], {'3'})

    def test_get_chain_valid_context(self):
        role_rel = [RoleRelation('Role', 'tenant', 'NY', 'District', 'School_1')]
        uc = UserContext(role_rel)
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY'})
        self.assertFalse(chain['all'])
        self.assertIn('District', chain['guid'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'District'})
        self.assertFalse(chain['all'])
        self.assertIn('School_1', chain['guid'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'District', 'schoolId': 'School_1'})
        self.assertTrue(chain['all'])

    def test_get_chain_tenant_level_context(self):
        role_rel = [RoleRelation('Role', 'tenant1', None, None, None)]
        uc = UserContext(role_rel)
        chain = uc.get_chain('tenant1', 'Role', {'stateCode': 'NC'})
        self.assertTrue(chain['all'])
        chain = uc.get_chain('tenant1', 'Role', {'stateCode': 'NC', 'districtId': '1234'})
        self.assertTrue(chain['all'])
        chain = uc.get_chain('tenant1', 'Role', {'stateCode': 'NC', 'districtId': '1234', 'schoolId': 'abcd'})
        self.assertTrue(chain['all'])

    def test_get_chain_state_level_context(self):
        role_rel = [RoleRelation('Role', 'tenant', 'NY', None, None)]
        uc = UserContext(role_rel)
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY'})
        self.assertTrue(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': '1234'})
        self.assertTrue(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': '1234', 'schoolId': 'abcd'})
        self.assertTrue(chain['all'])

    def test_get_chain_district_level_context(self):
        role_rel = [RoleRelation('Role', 'tenant', 'NY', '123', None)]
        uc = UserContext(role_rel)
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY'})
        self.assertFalse(chain['all'])
        self.assertIn('123', chain['guid'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': '123'})
        self.assertTrue(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': '123', 'schoolId': 'abcd'})
        self.assertTrue(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'aaa'})
        self.assertFalse(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'aaa', 'schoolId': 'abcd'})
        self.assertFalse(chain['all'])

    def test_get_chain_school_level_context(self):
        role_rel = [RoleRelation('Role', 'tenant', 'NY', '123', 'abcd')]
        uc = UserContext(role_rel)
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY'})
        self.assertFalse(chain['all'])
        self.assertIn('123', chain['guid'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': '123'})
        self.assertFalse(chain['all'])
        self.assertIn('abcd', chain['guid'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': '123', 'schoolId': 'abcd'})
        self.assertTrue(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'aaa'})
        self.assertFalse(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'aaa', 'schoolId': 'abcd'})
        self.assertFalse(chain['all'])

    def test_get_chain_invalid_context(self):
        role_rel = [RoleRelation('Role', 'tenant', 'NY', 'District', 'School_1')]
        uc = UserContext(role_rel)
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NC'})
        self.assertFalse(chain['all'])
        self.assertEqual(len(chain['guid']), 0)
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'District_2'})
        self.assertFalse(chain['all'])
        self.assertEqual(len(chain['guid']), 0)
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'District', 'schoolId': 'School_2'})
        self.assertFalse(chain['all'])
        self.assertEqual(len(chain['guid']), 0)
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'District_3', 'schoolId': 'School_2'})
        self.assertFalse(chain['all'])
        self.assertEqual(len(chain['guid']), 0)

    def test_get_chain_multi_context(self):
        role_rel = [RoleRelation('Role', 'tenant', 'NY', 'a', '1'),
                    RoleRelation('Role', 'tenant', 'NY', 'a', '2'),
                    RoleRelation('Role', 'tenant', 'NY', 'b', None)]
        uc = UserContext(role_rel)
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY'})
        self.assertFalse(chain['all'])
        self.assertIn('a', chain['guid'])
        self.assertIn('b', chain['guid'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'b'})
        self.assertTrue(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'b', 'schoolId': '3'})
        self.assertTrue(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'b', 'schoolId': '2'})
        self.assertTrue(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'a', 'schoolId': '2'})
        self.assertTrue(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'a', 'schoolId': '1'})
        self.assertTrue(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'a', 'schoolId': '3'})
        self.assertFalse(chain['all'])

    def test_get_chain_tenant_context_bad_tenant(self):
        role_rel = [RoleRelation('Role', 'tenant1', None, None, None)]
        uc = UserContext(role_rel)
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NC'})
        self.assertFalse(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NC', 'districtId': 'a'})
        self.assertFalse(chain['all'])
        chain = uc.get_chain('tenant', 'Role', {'stateCode': 'NC', 'districtId': 'a', 'schoolId': '1'})
        self.assertFalse(chain['all'])

    def test_get_chain_invalid_tenant(self):
        role_rel = [RoleRelation('Role', 'tenant', None, None, None)]
        uc = UserContext(role_rel)
        chain = uc.get_chain('bad_tenant', 'Role', {'stateCode': 'NY'})
        self.assertFalse(chain['all'])

    def test_get_chain_invalid_role(self):
        role_rel = [RoleRelation('Role', 'tenant', None, None, None)]
        uc = UserContext(role_rel)
        chain = uc.get_chain('tenant', 'bad_role', {'stateCode': 'NY'})
        self.assertFalse(chain['all'])

    def test_get_chain_invalid_request_param(self):
        role_rel = [RoleRelation('Role', 'tenant', None, None, None)]
        uc = UserContext(role_rel)
        chain = uc.get_chain('tenant', 'Role', {'bad': 'NY'})
        self.assertFalse(chain['all'])

    def test__get_default_permission(self):
        role_rel = [RoleRelation('Role', 'tenant', 'NY', None, None)]
        uc = UserContext(role_rel)
        perm = uc._get_default_permission()
        self.assertFalse(perm['all'])
        self.assertEqual(len(perm['guid']), 0)

    def test_validate_hierarchy(self):
        role_rel = [RoleRelation('Role', 'tenant', 'NY', 'a', None),
                    RoleRelation('Role', 'tenant', 'NY', 'b', None)]
        uc = UserContext(role_rel)
        result = uc.validate_hierarchy('tenant', 'Role', {'stateCode': 'NY'}, 'stateCode')
        self.assertFalse(result['all'])
        self.assertIn('a', result['guid'])
        self.assertIn('b', result['guid'])
        result = uc.validate_hierarchy('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'a'}, 'districtId')
        self.assertTrue(result['all'])
        result = uc.validate_hierarchy('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'b'}, 'districtId')
        self.assertTrue(result['all'])
        result = uc.validate_hierarchy('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'c'}, 'districtId')
        self.assertFalse(result['all'])
        result = uc.validate_hierarchy('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'c', 'schoolId': 'd'}, 'schoolId')
        self.assertFalse(result['all'])
        result = uc.validate_hierarchy('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'a', 'schoolId': 'd'}, 'schoolId')
        self.assertTrue(result['all'])
        result = uc.validate_hierarchy('tenant', 'Role', {'stateCode': 'NY', 'districtId': 'b', 'schoolId': 'd'}, 'schoolId')
        self.assertTrue(result['all'])

    def test__add_role(self):
        user = User()
        user._add_role('role')
        self.assertIn('role', user.get_roles())
        user._add_role(None)
        self.assertEqual(1, len(user.get_roles()))
        self.assertIn('role', user.get_roles())

    def test__add_tenant(self):
        user = User()
        user._add_tenant('t')
        self.assertIn('t', user.get_tenants())
        user._add_tenant(None)
        self.assertEqual(1, len(user.get_tenants()))
        self.assertIn('t', user.get_tenants())

    def test_default_permission_gets_added(self):
        role_rel = [RoleRelation('badrole', 'tenant', 'NY', 'a', '1'),
                    RoleRelation('PII', 'tenant', 'NY', 'a', '2'),
                    RoleRelation('badrole2', 'tenant', 'NY', 'b', None)]
        user = User()
        user.set_context(role_rel)
        roles = user.get_roles()
        self.assertEqual(2, len(roles))
        self.assertIn('DEFAULT', roles)
        self.assertIn('PII', roles)
        self.assertEqual(1, len(user.get_tenants()))

    def test_with_default_permission(self):
        role_rel = [RoleRelation('DEFAULT', 'tenant', 'NY', 'a', '1'),
                    RoleRelation('PII', 'tenant', 'NY', 'a', '1')]
        user = User()
        user.set_context(role_rel)
        roles = user.get_roles()
        self.assertEqual(2, len(roles))
        self.assertIn('DEFAULT', roles)
        self.assertIn('PII', roles)
        self.assertEqual(1, len(user.get_tenants()))

    def test_tenantless(self):
        role_rel = [RoleRelation('badrole', None, None, None, None),
                    RoleRelation('PII', 'tenant1', 'NC', 'a', '2')]
        user = User()
        user.set_context(role_rel)
        roles = user.get_roles()
        self.assertEqual(2, len(roles))
        self.assertIn('DEFAULT', roles)
        self.assertIn('PII', roles)
        tenants = user.get_tenants()
        self.assertEqual(3, len(tenants))

    def test_role_undefined(self):
        role_rel = [RoleRelation('invalidrole', None, None, None, None)]
        user = User()
        user.set_context(role_rel)
        roles = user.get_roles()
        self.assertEqual(1, len(roles))
        self.assertIn('DEFAULT', roles)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
