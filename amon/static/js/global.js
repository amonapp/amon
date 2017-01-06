$(document).ready(function () {


/**
 * setup JQuery's AJAX methods to setup CSRF token in the request before sending it off.
 * http://stackoverflow.com/questions/5100539/django-csrf-check-failing-with-an-ajax-post-request
 */

function getCookie(name)
{
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?

                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                        }
                }
        }
        return cookieValue;
}

$.ajaxSetup({
     timeout: 10000,
         beforeSend: function(xhr, settings) {
                 if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                         // Only send the token to relative URLs i.e. locally.
                         xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                 }
         }
});


// 2 options here - I can waste my day extending the options
// array and making it look pretty or I can just paste it ...
$('span.help-tooltip').each(function() {
    $(this).qtip({
        style: { classes: 'qtip-bootstrap' , "width": 450 },
        // position: {at: 'bottom center', my: 'right center'},
        content: {
            text: $(this).next('.qtip-tooltip')
        }

    });

});

// used on the server dashboard and in system
$('span.server-meta').each(function() {
    $(this).qtip({
        style: { classes: 'qtip-bootstrap' , "width": 350 },
        position: {at: 'right center', my: 'left top'},
        content: {
            text: $(this).next('.distro-tooltip')
        }
    });
});

window.show_notification = function(text){
    _.templateSettings = {interpolate : /\{\{(.+?)\}\}/g};
    var notifications_template = $('#notifications-template').text();
    var noti = _.template(notifications_template);

    rendered_notification = noti({message : text});

    $("body").append(rendered_notification);

    setTimeout(function() {
        $("#ajax-notification").remove();
    }, 3000);


}



});

$(document).ajaxError(function (event, xhr) {
        console.log(xhr.status + ': ' + xhr.statusText);
});

    var tooltip_options = {
        position: "top center",
        offset: [-4, 0],
    };


    var qtip_options = {
        style: { classes: 'qtip-bootstrap' , "width": 400 },
    }

    var action_options = $.extend(tooltip_options, {
        tipClass: 'action-tooltip'
    });

    $("#content .action a[title]").tooltip(action_options);
    $("#content .email_recipients, .sms_recipients, .tooltip__span").tooltip(tooltip_options);

    var qtip_options_title = {
        style: { classes: 'qtip-bootstrap' },
        position: {
            target: 'mouse',
            viewport: $(window)
        }
    }


    $("#content span[title]").qtip(qtip_options_title)


    $(".settings").tooltip({
        position: "bottom right",
        offset: [0, -93],
        tipClass: 'settings-tooltip'
    });


    $(".detailed-usage").tooltip({
        position: "center right",
        offset: [0, 10],
    });


function render_underscore_template(template, params){
    _.templateSettings = {interpolate : /\{\{(.+?)\}\}/g};

    var render = _.template(template)

    return render(params)

}


setTimeout(function() {
    $('.message-popup').addClass('slideInUp');

    setTimeout(function() {
        $('.message-popup').removeClass('slideInUp');
        $('.message-popup').addClass('slideOutDown');
    }, 3000);

    // $('.message-popup').removeClass('slideInUp').delay(1500).addClass('slideOutDown');
}, 500);




$('.message-popup--close').on('click', function(e){
    e.preventDefault();
    $('.message-popup').removeClass('slideInUp');
    $('.message-popup').addClass('slideOutDown');

});
