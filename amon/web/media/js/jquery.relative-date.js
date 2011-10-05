/**
* jQ plugin adapted from 37s' relative date tool
* Takes the format of "Jan 15, 2007 15:45:00 GMT" and converts it to a relative time
* @see http://37signals.com/svn/posts/1557-javascript-makes-relative-times-compatible-with-caching
*/
(function($, window, undefined){

    $.fn.relativeDate = function(opts){
        var defaults = {
            dateGetter: function(el){
                return $(el).text();
            }
        },
        options = $.extend({}, defaults, opts),
        time_ago_in_words_with_parsing = function(from) {
            var date = new Date;
            date.setTime(Date.parse(from));
            return time_ago_in_words(date);
        },
        time_ago_in_words = function(from) {
            return distance_of_time_in_words(new Date, from);
        },
        distance_of_time_in_words = function(to, from) {
            var distance_in_seconds = ((to - from) / 1000);
            var distance_in_minutes = Math.floor(distance_in_seconds / 60);

            if (distance_in_minutes == 0) { return 'less than a minute ago'; }
            if (distance_in_minutes == 1) { return 'a minute ago'; }
            if (distance_in_minutes < 45) { return distance_in_minutes + ' minutes ago'; }
            if (distance_in_minutes < 90) { return 'about 1 hour ago'; }
            if (distance_in_minutes < 1440) { return 'about ' + Math.round(distance_in_minutes / 60) + ' hours ago'; }
            if (distance_in_minutes < 2880) { return '1 day ago'; }
            if (distance_in_minutes < 43200) { return Math.floor(distance_in_minutes / 1440) + ' days ago'; }
            if (distance_in_minutes < 86400) { return 'about 1 month ago'; }
            if (distance_in_minutes < 525960) { return Math.floor(distance_in_minutes / 43200) + ' months ago'; }
            if (distance_in_minutes < 1051199) { return 'about 1 year ago'; }

            return 'over ' + Math.floor(distance_in_minutes / 525960) + ' years ago';
        }

        return $(this).each(function(){
            date_str = options.dateGetter(this);
            $(this).html(time_ago_in_words(date_str * 1000));
        });
    };

})(jQuery, window);
