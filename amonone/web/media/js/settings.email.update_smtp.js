$(document).ready(function () {

	var smtp_defaults = {
		"gmail" :{ 
			"address": "smtp.gmail.com",
			"port": 587,
			"security": "starttls"
		},
		"sendgrid": {
			"address": "smtp.sendgrid.net",
			"port": 587,
			"security": "none"
		},
		 "mandrill": {
			"address": "smtp.mandrillapp.com",
			"port": 587,
			"security": "none"
		}
	}

EmailSettingsView = Backbone.View.extend({
			
		el: $(".email-settings"),
			 
		events: {
			"change #smtp-template": "update_form",
		},

		initialize: function() {
			$("#smtp-template").select2({width: "250", minimumResultsForSearch: 100});
		},


		update_form: function(){
				default_values = {}
				value = $("#smtp-template").val();
				if(value in smtp_defaults) {
					default_values = smtp_defaults[value];
				}

				$("#update-form").find(':input').each(function(){
					 element = $(this).attr("id");
				
						if(element in default_values){ 
							$(this).val(default_values[element]);
						}
				});

				security = default_values["security"]
				$('#security-'+security).attr('checked', true);

		},

		
		
	});
	
	
	window.EmailSettingsView = new EmailSettingsView;

});