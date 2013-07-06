from os.path import join, abspath, dirname
import threading

from twilio.rest import TwilioRestClient
from jinja2 import Environment, FileSystemLoader

from amonone.utils.dates import dateformat_local
from amonone.sms.models import sms_model


def _send_sms_in_thread(client=None, from_=None, to=None, body=None):
	try:
		client.sms.messages.create(to=to,
									 from_=from_,
									  body=body)
	except Exception, e:
		raise e
		logging.exception("Can't send SMS")



def send_test_sms(recepient=None):
	details = sms_model.get()
	client = TwilioRestClient(details['account'], details['token'])

	t = threading.Thread(target=_send_sms_in_thread, 
				kwargs={"client": client,
					"from_": details['from_'],
					"to": recepient,
					"body": "Amon alert!"
				})
	t.start()


def render_template(alert=None, template=None):

		ROOT = abspath(dirname(__file__))
		TEMPLATES_DIR =  join(ROOT, 'templates')
		
		env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
		env.filters['date_local'] = dateformat_local


		template_file = env.get_template(template)		
		rendered_template = template_file.render(alert=alert)
		
		return rendered_template


def send_sms(alert=None, recepients=None, template=None):
	details = sms_model.get()
	
	try:
		client = TwilioRestClient(details['account'], details['token'])
	except:
		client = None
	
	
	if client != None:
		body = render_template(alert=alert, template=template)

		for recepient in recepients:
			t = threading.Thread(target=_send_sms_in_thread, 
				kwargs={"client": client,
					"from_": details['from_'],
					"to": recepient['phone'],
					"body": body
				}
			)
			t.start()