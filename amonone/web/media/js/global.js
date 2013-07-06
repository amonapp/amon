$(document).ready(function () {
	var tooltip_options = { 
		position: "top center",
		offset: [-4, 0]
	}

	var action_options = $.extend(tooltip_options, {
	    tipClass: 'action-tooltip'
	});

	$("#content .action a[title]").tooltip(action_options);
	$("#content span[title], .history").tooltip(tooltip_options);


	$(".logout").tooltip({ 
		position: "bottom center",
		offset: [-4, 0],
		tipClass: 'action-tooltip'
	});

});