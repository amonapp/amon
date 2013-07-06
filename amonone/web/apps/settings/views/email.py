from formencode.validators import Invalid as InvalidForm
from tornado.web import authenticated
from amonone.web.apps.core.baseview import BaseView

from amonone.mail.models import email_model, email_recepient_model
from amonone.mail.sender import send_mail
from amonone.web.apps.settings.forms import SMTPForm, EmailRecepientForm

class EmailBaseView(BaseView):
	def initialize(self):
		self.current_page = 'settings:email'
		super(EmailBaseView, self).initialize()

class EmailView(EmailBaseView):

	@authenticated
	def get(self, param=None):
	  
		server_details = email_model.get_email_details()
		recepients = email_recepient_model.get_all()
		self.render('settings/email/email.html',
				server_details=server_details,
				recepients=recepients)


class EmailUpdateView(EmailBaseView):

	@authenticated
	def get(self, param=None):
		errors =  self.session.get('errors',None)
		form_data =  self.session.get('form_data',None)
		server_details = email_model.get_email_details()

		self.delete_session_key('errors')
		self.delete_session_key('form_data')

		self.render('settings/email/update_smtp_details.html',
					server_details=server_details,
					errors=errors,
					form_data=form_data)


	@authenticated
	def post(self):
		form_data = {
				"address": self.get_argument('address', None),
				"port" : self.get_argument('port', None),         
				"username" : self.get_argument('username', None),         
				"password" : self.get_argument('password', None),         
				"from_" : self.get_argument('from', None),      
				"security": self.get_argument('security', None)
		}

		try:
			SMTPForm.to_python(form_data)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')
		
			email_model.save_email_details(form_data)
			self.redirect(self.reverse_url('settings_email'))
		
		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data
			self.redirect(self.reverse_url('update_email'))

class EmailAddRecepient(EmailBaseView):

	@authenticated
	def get(self):
		errors =  self.session.get('errors',None)
		form_data =  self.session.get('form_data',None)

		self.render('settings/email/add_recepient.html',
			errors=errors,
			form_data=form_data)

	@authenticated
	def post(self):
		form_data = {
				"name": self.get_argument('name', None),
				"email" : self.get_argument('email', None),         

		}

		try:
			EmailRecepientForm.to_python(form_data)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')
		
			email_recepient_model.insert(form_data)
			self.redirect(self.reverse_url('settings_email'))
		
		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data
			self.redirect(self.reverse_url('email_add_recepient'))


class EmailEditRecepientView(EmailBaseView):

	@authenticated
	def get(self, recepient_id=None):
		errors =  self.session.get('errors',None)
		form_data =  self.session.get('form_data',None)
	  
	  	recepient = email_recepient_model.get_by_id(recepient_id)

		self.render('settings/email/edit_recepient.html',
			recepient=recepient,
			errors=errors,
			form_data=form_data)

	@authenticated
	def post(self, recepient_id):
		form_data = {
				"name": self.get_argument('name', None),
				"email" : self.get_argument('email', None),         

		}

		try:
			EmailRecepientForm.to_python(form_data)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')
		
			email_recepient_model.update(form_data, recepient_id)
			self.redirect(self.reverse_url('settings_email'))
		
		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data
			self.redirect(self.reverse_url('email_edit_recepient', recepient_id))

class EmailDeleteRecepientView(EmailBaseView):

	@authenticated
	def get(self, recepient_id=None):
		email_recepient_model.delete(recepient_id)
		self.redirect(self.reverse_url('settings_email'))

class EmailTestView(EmailBaseView):

	@authenticated
	def get(self):
		message = self.get_session_key_and_delete('message')

		recepients = email_recepient_model.get_all()
		self.render('settings/email/test.html',
			message=message,
			recepients=recepients)

	@authenticated
	def post(self):
		recepient_id = self.get_argument('recepient', None)

		recepient = email_recepient_model.get_by_id(recepient_id)
	
		send_mail(recepients=[recepient],
			subject='Amon test email',
			template='test')

		self.session['message'] = 'Test email sent, check your inbox({0})'.format(recepient['email'])
		self.redirect(self.reverse_url('test_email'))