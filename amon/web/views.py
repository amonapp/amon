from template import render
import cherrypy
from db import _conn
from util import string_to_dict

class Dashboard:

	@cherrypy.expose
	def index(self):
	
		# get redis server info
		try:
			connection = _conn.info()
		except:
			connection = False

		# get the information from the last check
		try:
			latest_check = _conn.zrange('log', -1, -1)
			latest_check_dict = string_to_dict(latest_check[0])
		except:
			latest_check_dict = False

		return render(name="dashboard.html",
					  current_page='dashboard',
					  check=latest_check_dict,
					  connection=connection,
				)










