import unittest
from amonone.web.apps.core.acl import check_permissions, all_apps_for_user, all_servers_for_user
from nose.tools import eq_

class TestACL(unittest.TestCase):

	def test_admin_user(self):
		user = {"type": "admin"}
		result = check_permissions(False,'/something', user)
		eq_(True, result)

		# Page with id
		result = check_permissions('1234','/something', user)
		eq_(True, result)

		# Settings
		result = check_permissions('/settings','/settings', user)
		eq_(True, result)

	def test_readonly_user(self):
		user = {"type": "readonly", "apps":["app1", "app2"], "servers":["server1", "server2"]}
		result = check_permissions(False,'/system', user) # Parent pages - id is False
		eq_(True, result)

		result = check_permissions(False,'/', user) # Parent pages - id is False
		eq_(True, result)

		result = check_permissions(False,'/logs', user) # Parent pages - id is False
		eq_(True, result)

		result = check_permissions(False,'/something', user) # Parent pages - id is False
		eq_(True, result)

		result = check_permissions('server1','/system', user) # Page with server id
		eq_(True, result)

		result = check_permissions('serverdummy','/system', user) # Page with invalid server id
		eq_(False, result)
		
		result = check_permissions('server2','/processes', user) # Page with server id
		eq_(True, result)

		result = check_permissions('serverdummy','/processes', user) # Page with invalid server id
		eq_(False, result)

		result = check_permissions('app1','/logs', user) # Page with app id
		eq_(True, result)

		result = check_permissions('appdummy','/logs', user) # Page with invalid app id
		eq_(False, result)
		
		result = check_permissions('app2','/exceptions', user) # Page with app id
		eq_(True, result)

		result = check_permissions('appdummy','/exceptions', user) # Page with invalid app id
		eq_(False, result)

		result = check_permissions(False,'/settings', user) # Settings module
		eq_(False, result)

		result = check_permissions(False,'/settings/servers', user) # Settings module
		eq_(False, result)

		result = check_permissions(False,'/settings/users', user) # Settings module
		eq_(False, result)


	def test_filtered_apps_for_user(self):
		
		admin_user = {'type': 'admin'}
		result = all_apps_for_user(admin_user)
		eq_('all', result)

		readonly_user = {'type': 'readonly', 'apps': ['all']}
		result = all_apps_for_user(admin_user)
		eq_('all', result)

		readonly_user = {'type': 'readonly', 'apps': [1,2]}
		result = all_apps_for_user(readonly_user)
		eq_(result,[1, 2])

		readonly_user = {'type': 'readonly', 'apps': []}
		result = all_apps_for_user(readonly_user)
		eq_(result, False)

		none = None
		result = all_apps_for_user(none)
		eq_(result, False)


	def test_filtered_servers_for_user(self):

		admin_user = {'type': 'admin'}
		result = all_servers_for_user(admin_user)
		eq_('all', result)

		readonly_user = {'type': 'readonly', 'servers': ['all']}
		result = all_servers_for_user(admin_user)
		eq_('all', result)

		readonly_user = {'type': 'readonly', 'servers': [1,2]}
		result = all_servers_for_user(readonly_user)
		eq_(result,[1, 2])

		readonly_user = {'type': 'readonly', 'servers': []}
		result = all_servers_for_user(readonly_user)
		eq_(result, False)

		none = None
		result = all_servers_for_user(none)
		eq_(result, False)
