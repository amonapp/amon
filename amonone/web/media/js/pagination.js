$(document).ready(function () {
/* Format 

 <select name="page" id="pages-dropdown" data-url="">

*/
PaginationView = Backbone.View.extend({
	  
	el: $(".pagination"),
	   
	events: {
	  "change #pages-dropdown": "update_page",
	},

	initialize: function() {
		$('#pages-dropdown').select2({width: "70", minimumResultsForSearch: 300}); 
	},

	update_page: function(){
		select = $("#pages-dropdown");
		page = select.val();
		url = select.data('url');
		type = select.data('type');

		url_separator = "&";
		if(type == 'system'){
			url_separator = '?'
		}

		redirect_url = _.template("{{ url }}{{ url_separator }}page={{ page }}", [ url, url_separator, page ]);
		window.location.href = redirect_url;
	},
	
  });
  
  window.PaginationView = new PaginationView;

});