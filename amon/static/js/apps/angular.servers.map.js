"use strict";
angular.module('ServersMapApp', ['underscore', 'BaseModule'])
.directive('progressBar', function() {
    var el;

    return {
        restrict: 'A',
        scope: {},
        priority: 1,
        link: function(scope, element, attrs) {

            var percent = 1.2; // Container width -> 120px;
            var max_width = 120;

            el = element[0]

            var jq_obj = $(element[0]);
            

             var value = jq_obj.data('value');
            var total = jq_obj.data('total');
            var progress_width = 0;
             
            if(total !== undefined) {

                var percent_from_total = total/100;

                var width_in_percent = value/percent_from_total;
                progress_width = Math.floor((max_width/100) * width_in_percent);
            }
            else if(value > 0) {

                progress_width = Math.floor(percent*value);
            }

            // Avoid width overflows
            if(progress_width > max_width){
                progress_width = max_width;
            }

            
            jq_obj.css('width', progress_width);
            
            // Calculate critical values, more than 90%
            
            var progress_width_percent = Math.floor(progress_width/percent);

            if(progress_width_percent > 85) {
                jq_obj.addClass('red');
                jq_obj.siblings('span.data').addClass('red');
            }


        } // link

    }; // return
})


$.each($('.timeago'), function( index, value ) {
    var unix_timestamp = $(this).html();
    var moment_obj = moment.unix(unix_timestamp).fromNow();
    $(this).html(moment_obj)
        
});
$('a.plugin-error, .dashed, .timeago').each(function() {
    $(this).qtip({
        style: { classes: 'qtip-bootstrap' , "width": 200 },
        position: {at: 'bottom center', my: 'top center'},
        content: {
            text: $(this).next('.qtip-tooltip')
        }

    });

});
