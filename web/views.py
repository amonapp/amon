from template import render
import cherrypy



class Dashboard:

	@cherrypy.expose
	def index(self):
		return render(name="dashboard.html", current_page='dashboard')










