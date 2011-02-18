from template import render
import cherrypy
from db import _conn
from util import string_to_dict

class Dashboard:

	@cherrypy.expose
	def index(self):
	
		# test redis
		try:
			connection = _conn.info()
		except:
			connection = False

		
		if connection:
			latest_check = _conn.zrange('log', -1, -1)
			latest_check_dict = string_to_dict(latest_check[0])

			print latest_check_dict

		return render(name="dashboard.html",
					  current_page='dashboard',
					  check=latest_check_dict,
				)










