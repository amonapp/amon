from tornado.web import authenticated
from amonone.web.apps.core.baseview import BaseView
from formencode.validators import Invalid as InvalidForm
from amonone.web.apps.alerts.models import alerts_model
from amonone.web.apps.core.models import server_model
from amonone.web.settings import (
	process_metrics, server_metrics, common_metrics
)
from amonone.web.apps.alerts.forms import (
	AddServerRuleForm, AddProcessRuleForm,
	EditServerRuleForm, EditProcessRuleForm,
)
from amonone.mail.models import email_recepient_model
from amonone.sms.models import sms_recepient_model


class AlertsView(BaseView):
	def initialize(self):
		self.current_page = 'alerts'
		super(AlertsView, self).initialize()

	@authenticated
	def get(self):

		system_alerts = alerts_model.get_alerts(type='server')
		process_alerts = alerts_model.get_alerts(type='process')

					
		self.render('alerts/view.html',	
				process_metrics=process_metrics,
				server_metrics=server_metrics,
				common_metrics=common_metrics,
				system_alerts=system_alerts,
				process_alerts=process_alerts	
				)

class AddSystemAlertView(BaseView):

	def initialize(self):
		self.current_page = 'alerts'
		super(AddSystemAlertView, self).initialize()

	@authenticated
	def get(self):

		server = server_model.get_one()

		errors =  self.session.get('errors',None)
		form_data =  self.session.get('form_data',None)
		email_recepients = email_recepient_model.get_all()
		sms_recepients = sms_recepient_model.get_all()

		self.delete_session_key('errors')
		self.delete_session_key('form_data')

		self.render('alerts/add_server_alert.html',
				email_recepients=email_recepients,
				sms_recepients=sms_recepients,
				process_metrics=process_metrics,
				server_metrics=server_metrics,
				common_metrics=common_metrics,
				errors=errors,
				server=server,
				form_data=form_data
		)


	@authenticated
	def post(self):
		form_data = {
				"metric" : self.get_argument('metric', None),         
				"metric_value" : self.get_argument('metric_value', None),         
				"above_below" : self.get_argument('above_below', None),         
				"metric_type": self.get_argument('metric_type', None),
				"metric_options": self.get_argument('metric_options',None),
				"threshold": self.get_argument('threshold', None),
				"email_recepients": self.get_arguments('email', None),
				"sms_recepients": self.get_arguments('sms', None),
				"rule_type": 'server'
		}
		
		try:
			AddServerRuleForm.to_python(form_data)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')
		
			alerts_model.save(form_data)
			self.redirect(self.reverse_url('alerts'))
		
		except InvalidForm, e:
			print e.unpack_errors()
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data
			self.redirect(self.reverse_url('add_server_alert'))


class DeleteServerAlertView(BaseView):

	def initialize(self):
		super(DeleteServerAlertView, self).initialize()

	@authenticated
	def get(self, param=None):
		alerts_model.delete(param)
		self.redirect(self.reverse_url('alerts'))

class AddProcessAlertView(BaseView):

	def initialize(self):
		self.current_page = 'alerts'
		super(AddProcessAlertView, self).initialize()

	@authenticated
	def get(self):

		server = server_model.get_one()
		
		errors =  self.session.get('errors',None)
		form_data =  self.session.get('form_data',None)
		email_recepients = email_recepient_model.get_all()
		sms_recepients = sms_recepient_model.get_all()


		self.delete_session_key('errors')
		self.delete_session_key('form_data')

		self.render('alerts/add_process_alert.html',
				email_recepients=email_recepients,
				sms_recepients=sms_recepients,
				process_metrics=process_metrics,
				errors=errors,
				form_data=form_data,
				server=server
		)


	@authenticated
	def post(self):
		form_data = {
				"process" : self.get_argument('process', None),  
				"above_below" : self.get_argument('above_below', None),  
				"check" : self.get_argument('check', None),        
				"metric_value" : self.get_argument('metric_value', None),         
				"metric_type" : self.get_argument('metric_type', None),                         
				"threshold": self.get_argument('threshold', None),
				"email_recepients": self.get_arguments('email', None),
				"sms_recepients": self.get_arguments('sms', None),
				"rule_type": 'process'
		}

		try:
			AddProcessRuleForm.to_python(form_data)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')
		
			alerts_model.save(form_data)
			self.redirect(self.reverse_url('alerts'))
		
		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data
			self.redirect('/alerts/process')

class DeleteProcessAlertView(BaseView):

	def initialize(self):
		super(DeleteProcessAlertView, self).initialize()

	@authenticated
	def get(self, param=None):
		alerts_model.delete(param)
		self.redirect(self.reverse_url('alerts'))


class EditServerAlertView(BaseView):

	def initialize(self):
		self.current_page = 'alerts'
		super(EditServerAlertView, self).initialize()

	@authenticated
	def get(self, alert_id):
		alert = alerts_model.get_by_id(alert_id)

		server = server_model.get_one()

	
		errors =  self.session.get('errors',None)
		form_data =  self.session.get('form_data',None)
		email_recepients = email_recepient_model.get_all()
		sms_recepients = sms_recepient_model.get_all()

		self.delete_session_key('errors')
		self.delete_session_key('form_data')

		self.render('alerts/edit_server_alert.html',
				alert=alert,
				email_recepients=email_recepients,
				sms_recepients=sms_recepients,
				process_metrics=process_metrics,
				server_metrics=server_metrics,
				common_metrics=common_metrics,
				errors=errors,
				form_data=form_data,
				server=server
		)


	@authenticated
	def post(self, alert_id):
		form_data = {      
				"metric_value" : self.get_argument('metric_value', None),         
				"above_below" : self.get_argument('above_below', None),         
				"metric_type": self.get_argument('metric_type', None),
				"metric_options": self.get_argument('metric_options',None),
				"threshold": self.get_argument('threshold', None),
				"email_recepients": self.get_arguments('email', None),
				"sms_recepients": self.get_arguments('sms', None),
				"rule_type": 'server'
		}
		
		try:
			EditServerRuleForm.to_python(form_data)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')
		
			alerts_model.update(form_data, alert_id)
			alerts_model.clear_alert_history(alert_id)
			self.redirect(self.reverse_url('alerts'))
		
		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data
			self.redirect(self.reverse_url('edit_server_alert', alert_id))



class EditProcessAlertView(BaseView):

	def initialize(self):
		self.current_page = 'alerts'
		super(EditProcessAlertView, self).initialize()

	@authenticated
	def get(self, alert_id):
		alert = alerts_model.get_by_id(alert_id)

	
		errors =  self.session.get('errors',None)
		form_data =  self.session.get('form_data',None)
		email_recepients = email_recepient_model.get_all()
		sms_recepients = sms_recepient_model.get_all()

		self.delete_session_key('errors')
		self.delete_session_key('form_data')

		self.render('alerts/edit_process_alert.html',
				alert=alert,
				email_recepients=email_recepients,
				sms_recepients=sms_recepients,
				process_metrics=process_metrics,
				server_metrics=server_metrics,
				common_metrics=common_metrics,
				errors=errors,
				form_data=form_data
		)


	@authenticated
	def post(self, alert_id):
		form_data = {      
			"metric_value" : self.get_argument('metric_value', None),         
			"above_below" : self.get_argument('above_below', None),         
			"metric_type": self.get_argument('metric_type', None),
			"metric_options": self.get_argument('metric_options',None),
			"threshold": self.get_argument('threshold', None),
			"email_recepients": self.get_arguments('email', None),
			"sms_recepients": self.get_arguments('sms', None),
			"rule_type": 'process'
		}
		
		try:
			EditProcessRuleForm.to_python(form_data)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')
			
			alerts_model.update(form_data, alert_id)
			alerts_model.clear_alert_history(alert_id)
			self.redirect(self.reverse_url('alerts'))
		
		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data
			self.redirect(self.reverse_url('edit_process_alert', alert_id))


class MuteAlertView(BaseView):
	def initialize(self):
		self.current_page = 'alerts'
		super(MuteAlertView, self).initialize()

	@authenticated
	def get(self, rule_id=None):
		alert = alerts_model.get_by_id(rule_id)

		alert_type = alert.get('rule_type', 'server')
		alerts_model.mute(rule_id)

		redirect_url = self.reverse_url('alerts')

		self.redirect(redirect_url)


class AlertHistoryView(BaseView):
	def initialize(self):
		self.current_page = 'alerts'
		super(AlertHistoryView, self).initialize()

	@authenticated
	def get(self, alert_id):
		
		alert = alerts_model.get_by_id(alert_id)
		
		page = self.get_argument('page', 1)

		alert_history = alert.get('history', {})
		history = self.paginate(alert_history, page=page)

		self.render('alerts/history.html',
			history=history,
			alert=alert)

class ClearAlertHistoryView(BaseView):
	def initialize(self):
		self.current_page = 'alerts'
		super(ClearAlertHistoryView, self).initialize()

	@authenticated
	def get(self, alert_id):
		alerts_model.clear_alert_history(alert_id)
		self.redirect(self.reverse_url('alert_history', alert_id))