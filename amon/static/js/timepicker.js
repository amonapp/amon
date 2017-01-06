$(function () 
{    

    max_date = $('#now_local').val();
    max_date_value = moment(max_date, "DD.MM.YYYY HH:mm").toDate();

    min_date = $('#first_check_date').val();
    min_date_value = moment(min_date, "DD.MM.YYYY HH:mm").toDate();
    

    $('a#custom-range').on("click", function (e) {
        e.preventDefault();
        $("#overlay").addClass('open');
    })

    $('#close-timepicker').on('click', function (e){
        e.preventDefault();

        $("#overlay").removeClass('open');
    });

    var date_options = {
        format: 'dd.mm.yyyy',
        max: max_date_value,
        min: min_date_value,
        selectMonths: true
    }


    var date_from = $('.date_from').pickadate(date_options);
    var time_from = $('.time_from').pickatime({formatLabel: 'HH:i', format: 'HH:i'});


    var date_to = $('.date_to').pickadate(date_options);
    var time_to = $('.time_to').pickatime({formatLabel: 'HH:i', format: 'HH:i'});



    $('form#update_daterange').on('submit', function (e) {
        e.preventDefault();

        values = $(this).serializeArray();
        values_array = {};

        $(values).each(function(i, field){
          values_array[field.name] = field.value.trim();
        });
        


        var date_time_from = render_underscore_template('{{ date_from }}-{{ time_from }}', 
                { date_from: values_array['date_from'], time_from: values_array['time_from'] });
        
        var date_time_to = render_underscore_template('{{ date_to }}-{{ time_to }}', 
            { date_to: values_array['date_to'], time_to: values_array['time_to'] });

        parsed_from = moment.utc(date_time_from, "DD.MM.YYYY-HH:mm").unix(); 
        parsed_to = moment.utc(date_time_to, "DD.MM.YYYY-HH:mm").unix(); 

        duration = parsed_to-parsed_from;
        enddate = parsed_to;

        // Convert the date to Unix with Django, momentjs is just horrible with timezones.
        base_url = $("#custom-range").data('url');
        convert_to_unix_url = $('#timezone_url').val();
        $.get(convert_to_unix_url, { date_to_local: date_time_to} )
             .done(function(data) {
                 unixtime = data.unixtime
                   
                   goto_url = render_underscore_template('{{ base_url }}&duration={{ duration }}&enddate={{ enddate }}', 
                { base_url: base_url, duration: duration, enddate: unixtime });

                window.location.href = goto_url;
        });
        
    
        
        
    })
});