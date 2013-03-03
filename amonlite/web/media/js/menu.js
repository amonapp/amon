$(document).ready(function(){

var menu = $('#menu'),
	pos = menu.offset();
		
	$(window).scroll(function(){
		if($(this).scrollTop() > pos.top+menu.height() && menu.hasClass('default')){
			menu.fadeOut('fast', function(){
				$(this).removeClass('default').addClass('fixed').fadeIn('fast');
			});
		} else if($(this).scrollTop() <= pos.top && menu.hasClass('fixed')){
			menu.fadeOut('fast', function(){
				$(this).removeClass('fixed').addClass('default').fadeIn('fast');
			});
		}
	});

});
