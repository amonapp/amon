"use strict";
angular.module('ServersApp', ['underscore', 'BaseModule'])
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
.directive('serversTagsDropdown', function(Select2Options, Requests, _, Template) {
    var el;
    return {
        restrict: 'A',
        scope: {},
        link: function(scope, element, attrs) {
            el = $(element);
            var options = Select2Options.array(el); 
            el.select2({
                width: options.size, 
                minimumResultsForSearch: 5, 
                placeholder: options.placeholder, 
                tags: true,
                ajax: {
                    url: options.url,
                    dataType: 'json',
                    data: function(term, page) {
                        return {
                            q: term
                        };
                    },
                    results: function(data, page) {
                        
                        return {

                            results: data
                        };
                    }
                },

                // Some nice improvements:
                maximumSelectionSize: 5,

                // override message for max tags
                formatSelectionTooBig: function (limit) {
                    return "Max tags is only " + limit;
                },

                // Only in edit, else empty
                initSelection: function (element, callback) {
                    var selected_tags = [];
                    var tags = element.val().split(',');

                    // Get all tags, eliminate
                    Requests.get(options.url, tags).then(function(data){
                        
                        _.each(data, function(el){
                            if(_.contains(tags, el.id)){
                                
                                selected_tags.push({
                                    id: el.id,
                                    text: el.text
                                });
                            }
                        
                        });

                        callback(selected_tags);
                    })

                    

                    
                },
            


            }); //select2 end

            el.on("change", function(element) {
                var data_url = el.data('page-url');
                var tags = element.val.join(',');

                if(tags.length > 0){
                    data_url = Template("{{{url}}}?tags={{ tags }}", 
                    {url: data_url, tags: tags,})
                }
                
                    
                window.location.href = data_url
                
            });

            
        

        } // link

    }; // return
})