$(document).ready(function () {

	SMSTestModel = Backbone.Model.extend({
		initialize: function() {}
	});

	SMSTestSettingsView = Backbone.View.extend({
			
		el: $(".sms-test"),
			 
		events: {
			"submit #test-sms-form": "submit_form",
		},

		initialize: function() {
			$("#recepient-select").select2({width: "300", minimumResultsForSearch: 100});
			this.model = new SMSTestModel;
			this.model.view = this;
		},


		submit_form: function(event){
			event.preventDefault();
			
			var form_data = form2object('test-sms-form', '.', true);

			form = $(event.currentTarget);
			this.model.url = form.data('url');

			this.model.save(form_data);
			this.model.clear();

		},

		
		
	});
	
	
	window.SMSTestSettingsView = new SMSTestSettingsView;

});