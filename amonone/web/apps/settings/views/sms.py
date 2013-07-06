from formencode.validators import Invalid as InvalidForm
from tornado.web import authenticated
from tornado import escape as tornado_escape
from amonone.web.apps.core.baseview import BaseView

from amonone.sms.models import sms_model, sms_recepient_model
from amonone.web.apps.settings.forms import SMSForm, SMSRecepientForm
from amonone.sms.sender import send_test_sms

class SMSBaseView(BaseView):
	def initialize(self):
		self.current_page = 'settings:sms'
		super(SMSBaseView, self).initialize()

class SMSView(SMSBaseView):

	@authenticated
	def get(self, param=None):
		details = sms_model.get()
		recepients = sms_recepient_model.get_all()
		self.render('settings/sms/sms.html', details=details,
			recepients=recepients)

class SMSTestView(SMSBaseView):

	@authenticated
	def get(self, param=None):
		recepients = sms_recepient_model.get_all()
		self.render('settings/sms/test.html',
			recepients=recepients)

	@authenticated
	def post(self):
		post_data = tornado_escape.json_decode(self.request.body)

		recepient_param = post_data.get('recepient')
		recepient = sms_recepient_model.get_by_id(recepient_param)
		
		response = send_test_sms(recepient=recepient['phone'])
		

		

class SMSUpdateView(SMSBaseView):

	@authenticated
	def get(self, param=None):
		errors =  self.session.get('errors',None)
		form_data =  self.session.get('form_data',None)
		details = sms_model.get()

		self.delete_session_key('errors')
		self.delete_session_key('form_data')

		self.render('settings/sms/update_sms_details.html',
					details=details,
					errors=errors,
					form_data=form_data)


	@authenticated
	def post(self):
		form_data = {
				"account": self.get_argument('account', None),
				"token" : self.get_argument('token', None),
				"from_" : self.get_argument('from', None), 
		}

		try:
			SMSForm.to_python(form_data)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')
		
			sms_model.save(form_data)
			self.redirect(self.reverse_url('settings_sms'))
		
		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data
			self.redirect('/settings/sms/edit')


class SMSAddRecepient(SMSBaseView):

	@authenticated
	def get(self):
		errors =  self.session.get('errors',None)
		form_data =  self.session.get('form_data',None)

		self.render('settings/sms/add_recepient.html',
			errors=errors,
			form_data=form_data)

	@authenticated
	def post(self):
		form_data = {
				"name": self.get_argument('name', None),
				"phone" : self.get_argument('phone', None),         

		}

		try:
			SMSRecepientForm.to_python(form_data)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')
		
			sms_recepient_model.insert(form_data)
			self.redirect(self.reverse_url('settings_sms'))
		
		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data
			self.redirect(self.reverse_url('sms_add_recepient'))


class SMSEditRecepientView(SMSBaseView):

	@authenticated
	def get(self, recepient_id=None):
		errors =  self.session.get('errors',None)
		form_data =  self.session.get('form_data',None)
	  
	  	recepient = sms_recepient_model.get_by_id(recepient_id)

		self.render('settings/sms/edit_recepient.html',
			recepient=recepient,
			errors=errors,
			form_data=form_data)

	@authenticated
	def post(self, recepient_id):
		form_data = {
				"name": self.get_argument('name', None),
				"phone" : self.get_argument('phone', None),
		}

		try:
			SMSRecepientForm.to_python(form_data)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')
		
			sms_recepient_model.update(form_data, recepient_id)
			self.redirect(self.reverse_url('settings_sms'))
		
		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data
			self.redirect(self.reverse_url('sms_edit_recepient', recepient_id))

class SMSDeleteRecepientView(SMSBaseView):

	@authenticated
	def get(self, recepient_id=None):
		sms_recepient_model.delete(recepient_id)
		self.redirect(self.reverse_url('settings_sms'))