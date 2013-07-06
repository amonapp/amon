def check_permissions(id, page, user):
	if user['type'] == 'admin':
		return True
	
	# Settings, only admin users
	if page.startswith('/settings'):
			return False

	# Alerts, only admin users
	if page.startswith('/alerts'):
			return False
	
	# Parent pages - no ids
	if id == False:
		return True

	if page in ['/system','/processes']:
		servers = user.get('servers', None)
		if id in servers:
			return True
		else:
			return False


	return False

def all_servers_for_user(user):
	if user is None:
		return False

	user_type = user.get('type', None)
	
	if user_type == 'admin':
		return 'all'
	if user_type == 'readonly':
		servers = len(user['servers'])
		# Empty list
		if servers == 0:
			return False
		# List with apps
		if servers > 1:
			return user['servers']
		# Check if the user has permission for all apps
		if servers == 1 and user['servers'][0] == 'all':
			return 'all'
		# Default
		else:
			return user['servers']

	return False




