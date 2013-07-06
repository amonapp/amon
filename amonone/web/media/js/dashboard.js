$(function () 
{
	
	percent = 1.25; // Container width -> 120px;
	max_width = 125;

	$.each($('span.progress'), function() {
		el = $(this);
		value = el.data('value');
		total = el.data('total');
		var progress_width = 0;
		
		if(total != undefined) {

			percent = total/100;

			width_in_percent = value/percent;
			var progress_width = Math.floor((max_width/100) * width_in_percent)
		}
		else if(value > 0) {

			var progress_width = Math.floor(percent*value);
		}

		el.css('width', progress_width);
		
		
	});
});