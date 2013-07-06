
from amonone.core import settings
from amonone.web.apps.core.baseview import BaseView

class AgentView(BaseView):
    
    def get(self):

        server_key = self.get_argument('server_key', 'Insert your server key here')
        host = settings.WEB_APP['host']
        port = settings.WEB_APP['port']

        full_url = "{0}:{1}".format(host, port)

        self.render('agent.sh', full_url=full_url, 
                                host=host, port=port,
                                server_key=server_key)
