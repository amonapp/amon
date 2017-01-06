"use strict";
$(function ()
{

    var process_table_options = {
        "bPaginate": false,
        "bLengthChange": false,
        "bInfo": false,
        "bAutoWidth": false,
        "oLanguage": {"sSearch": "",},
        "ordering": true,
        "order": [[ 2, "desc" ]],
   }

   var containers_table_options = {
        "bPaginate": false,
        "bLengthChange": false,
        "bInfo": false,
        "bAutoWidth": false,
        "filter": false,
        "oLanguage": {"sSearch": "",},
        "ordering": true,
        "order": [[ 2, "desc" ]],
   }

   var process_table_columns = [
       {
            "data": "name",
        },
        {
           "data": "cpu",
           "render": function (data, type) {
                return type === 'display' ? data+"%" : data;
            }
       },
       {
            "data": "memory",
             "render": function (data, type) {
              return type === 'display' ? data+"MB" : data;
             }
        },
         {
            "data": "io",

             "render": function (data, type) {
              return type === 'display' ? data+"KB" : data;
             }
        },
        {
          "data": "url",
         "render": function (data, type) {
            var n = data.search("monitor");
            var link;

            if(n >= 0) {
                link = Mustache.render("<a href='#' class='monitor-ignored-process' data-url='{{url}}'>Monitor</a>", {url:data});
            }
            else {
                link = Mustache.render("<a href='{{url}}'>View chart</a>", {url:data});
            }

            return type === 'display' ? link : data;
        }
    }];

    process_table_options['columns'] = process_table_columns;




    var server_table;
    var process_table;


    function render_process_table(id, url, type) {
        var table_id = "#processes-table-"+id;
        process_table_options['ajax'] = url;


        var filter_id = table_id+'_filter';
        var process_table = $(table_id).DataTable(process_table_options);
        $(filter_id).find('input').attr("placeholder", "Process filter");
    }




    function open_details_row(id, html, type, url) {
        var current_row_object = $('#row-'+id);
        var row = server_table.row(current_row_object);

        // Opens a row with more details
        function _show_row() {
            row.child(html).show();

            if(type === 'processes'|| type === 'ignored') {
                render_process_table(id, url, type);
            }



            current_row_object.find('.processes-row a').removeClass('active');
            current_row_object.find('.processes-row a.' + type).addClass('active');

            $.each(['install', 'processes', 'ignored', 'containers'], function(i, v){
                current_row_object.removeClass(v);
            })

            current_row_object.addClass(type);
        }

        if (row.child.isShown()) {
            row.child.hide();
            current_row_object.find('.processes-row a.' + type).removeClass('active');
            // The user clicked the same button, just remove the class
            // The user clicked the same button, just remove the class
            if(!current_row_object.hasClass(type)) {
                _show_row()
            }


        }
        else {
            // Open this row
            _show_row()
        }


    }

    $(document).on('click', 'a.toggle-processes-table', function (e) {
        e.preventDefault();
        var id = $(this).data('id');
        var url = $(this).data('url');

        var processes_table_html = $("#processes-"+id).html();
        var details_type = $(this).data('type');


        open_details_row(id, processes_table_html, details_type, url);
    });



    var server_table = $(".server_filter").DataTable({
        "bPaginate": false,
        "bLengthChange": false,
        "bFilter": true,
        // "fixedHeader": {
  //           "footer": true
  //           },
        "bSort": true,
        "bInfo": false,
        "bAutoWidth": false,
        //"bJQueryUI": true,
        "bStateSave": true,
         "oLanguage": {
            "sSearch": "",
        },
        "sDom": 'rt',
         "aoColumns": [
            null,
            { "bSearchable": false },

            { "bSearchable": false },
            { "bSearchable": false },
            { "bSearchable": false },
            null,
            null,
            null
        ],
         "aaSorting": [ [6,'desc'],],

    })

    $('#server_filter').keyup(function(){
        server_table.search($(this).val()).draw() ;
    })


    if(window.location.hash) {
        var id = window.location.hash.substring(1);
        var install_table_html = $("#install-"+id).html();
        var details_type = 'install'

        open_details_row(id, install_table_html, details_type);

        var current_row_object = $('#row-'+id);
        $('body').scrollTo(current_row_object.offset().top, 50 );

    }


    $('.server_filter').on('click', 'a.toggle-install-table', function(event) {
        event.preventDefault();
        var id = $(this).data('id');

        var install_table_html = $("#install-"+id).html();
        var details_type = 'install'

        open_details_row(id, install_table_html, details_type);

        history.pushState("", document.title, window.location.pathname); // remove the hash from the url

    });


    $(document).on('click', 'a.monitor-ignored-process', function (e) {
        e.preventDefault();
        var url = $(this).data('url');

        var parsed = purl(url).param();
        var message = Mustache.render("Monitoring for {{ name }} enabled. ", {name:parsed.name});


        $.get(url)
            .done(function(data) {
                window.show_notification(message)

                var row = process_table.row( $(this).parents('tr') );
                row.remove().draw();
        });


    });


     // Find empty tooltips and hide them
     $.each($('div.distro-tooltip'), function() {
        var el = $(this);
        var metadata = el.find('ul').children().length;

            if(metadata == 0){
                el.remove();
            }
    });




    var qtip_options = {
        style: { classes: 'qtip-bootstrap' , "width": 400 },
         position: {
            at: 'left bottom'
        }
    }

    // used on the server dashboard and in system
    $('span.server-meta').each(function() {
        $(this).qtip({
            style: { classes: 'qtip-bootstrap' , "width": 350 },
            // position: {at: 'right center', my: 'left top'},
            content: {
                text: $(this).next('.distro-tooltip')
            }
        });
    });


    // 2 options here - I can waste my day extending the options
    // array and making it look pretty or I can just paste it ...
    $('a.plugin-error, .dashed, .last_check').each(function() {
        $(this).qtip({
            style: { classes: 'qtip-bootstrap' , "width": 250 },
            position: {at: 'bottom center', my: 'right center'},
            content: {
                text: $(this).next('.qtip-tooltip')
            }

        });

    });


    $(document).on('click', 'a.install-agent', function (e) {
        e.preventDefault();
        $("#install-agent").toggleClass('visible')
    });
    $(document).on('click', 'a.toggle-install-agent-close-button', function (e) {
        e.preventDefault();
        $("#install-agent").toggleClass('visible')
    });



});
