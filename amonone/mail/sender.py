from os.path import join, abspath, dirname

from mailtools import SMTPMailer, ThreadedMailer
from jinja2 import Environment, FileSystemLoader
from tornado import escape

from amonone.mail.models import email_model
from amonone.utils.dates import dateformat_local


def send_mail(recepients=None, subject=None, template=None,  template_data=None):
	connection_details = email_model.get_email_details()

	port = int(connection_details['port'])
	security = connection_details['security'] if connection_details['security'] != 'None' else None

	mailer = ThreadedMailer(SMTPMailer(connection_details['address'], port, 
					username = connection_details['username'],
					password = connection_details['password'],
					transport_args = {'security': security},
					log_file = '/var/log/amonone/amonone-mailer.log',
					log_messages=False))


	EMAIL_ROOT = abspath(dirname(__file__))
	TEMPLATES_DIR =  join(EMAIL_ROOT, 'templates')

	env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
	env.filters['date_local'] = dateformat_local

	template_file = env.get_template("{0}.html".format(template))
	rendered_template = template_file.render(template_data=template_data)

	message = escape.to_unicode(rendered_template)

	subject = escape.to_unicode(subject)

	email_recepients = [x['email'] for x in recepients]

	try: 
		mailer.send_html(connection_details['from_'], email_recepients, subject, message)
	except Exception, e:
		print e
		raise e 



