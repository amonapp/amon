"use strict";
angular.module('RickshawApp', ['underscore', 'BaseModule']);

angular.module('RickshawApp')
.factory('RickshawTimeFixtures', function($rootScope){
    var timestamp;
    var timeunit;
    var timefixture = new Rickshaw.Fixtures.Time();

    timefixture.formatTime = function(d) {

        timestamp = window.moment(d).utc().format("HH:mm");
        return timestamp;
    }

    timefixture.units.push({
        name: 'five_minutes',
        seconds: 60 * 5,
        formatter: function(d) { return timefixture.formatTime(d)}
    })

    timefixture.units.push({
        name: 'fifteen_minutes',
        seconds: 60 * 15,
        formatter: function(d) { return timefixture.formatTime(d)}
    })

    timefixture.units.push({
        name: 'thirty_minutes',
        seconds: 60 * 30,
        formatter: function(d) { return timefixture.formatTime(d)}
    })

    timefixture.units.push({
        name: 'two_minutes',
        seconds: 60 * 2,
        formatter: function(d) { return timefixture.formatTime(d)}
    })

    return {
            SetTimeUnit: function(duration){

                var time_units = [
                    'two_minutes',             // 0 
                    'five_minutes',          // 1
                    'fifteen_minutes',      // 2
                    'thirty_minutes',         // 3
                    'hour',                 // 4 
                    '6 hour'                 // 5
                ]

                var selected_unit;
                if(duration <= 1800){
                    selected_unit = 0
                }
                else if(duration > 1800 && duration < 10800) { // 30 minutes - 3 hours
                    selected_unit = 1
                }
                else if(duration >= 10800 && duration < 21600) { // 3-6 hours
                    selected_unit = 2
                }
                else if(duration >= 21600 && duration < 43200){  // 6-12 hours
                    selected_unit =3
                }
                else if(duration >= 43200 && duration <= 86400){  // 12-24 hours
                    selected_unit =4
                }
                else if(duration > 86400){  // 12-24 hours
                    selected_unit = 5
                }

                // TODO - Add formatting for days
                if($rootScope.size == 'S' || $rootScope.size == 'M') {
                    selected_unit = selected_unit+1;
                }

                selected_unit = (selected_unit > 5) ? 5 : selected_unit;
                timeunit = timefixture.unit(time_units[selected_unit])
            
                return timeunit;
            }
    }
})
.factory('RickshawGraphSize', function($rootScope){
    return{
        width: function(chart_el){

            var padding = 40;
            
            var content_width = $('body')[0].offsetWidth-padding;

            var element_width = parseInt(content_width);
            
            if($rootScope.size == 'M') {
                element_width = parseInt(content_width)/2
            }
            else if($rootScope.size == 'S') {
                element_width = parseInt(content_width)/3
            }

            // This is present only in custom metrics, will be extended, fit chart in this block
            var chart_wrapper = $('.chart-wrapper');
            if(chart_wrapper.length > 0){
                element_width = chart_wrapper[0].offsetWidth;
            }
            
            var graph_width = element_width-70;

            return {
                'el': element_width,
                'graph': graph_width
            }
        }
    } // return 
})
.controller('RickshawSizer', function($scope, $rootScope, $window){
    $rootScope.size  = 'M';
    $scope.sizes = ['S','M','L'];


    var size_param = $.url().param('size') || false; // parse the current page URL

    $scope.init = function(charts_on_page) {
        if(parseInt(charts_on_page) == 1){
            $rootScope.size  = 'L';
        }

        if(parseInt(charts_on_page) == 2){
            $rootScope.size  = 'M';
        }

        if(size_param != false){
            if($scope.sizes.indexOf(size_param) > -1) {
                $rootScope.size = size_param.toUpperCase();
            }
            
        }
        
     };

     $scope.define_size = function(){
         if($rootScope.charts_on_page != undefined){
             
             if(parseInt($rootScope.charts_on_page) == 1){
                $rootScope.size  = 'L';
            }

            if(parseInt($rootScope.charts_on_page) == 2){
                $rootScope.size  = 'M';
            }

            if(parseInt($rootScope.charts_on_page) >= 3){
                $rootScope.size  = 'S';
            }
         }
         else {
             $rootScope.size = 'L'
         }
     }

    

    $scope.set_size = function(new_size) {
        $rootScope.size = new_size;
        $rootScope.$broadcast("setchartsize");
    }

    $scope.set_class = function(size) {
        if(size === $rootScope.size){
            return 'active';
        }
    }

    $scope.set_class($rootScope.size);
    $scope.set_size($rootScope.size);

    $scope.$on("resize_charts", function () {
        $scope.define_size();
        $rootScope.$broadcast("setchartsize");
    });

    
    
})
.controller('RickshawChartNoData', function($scope, $rootScope) {
    $rootScope.empty_charts = [];
})
.controller('RickshawTimer', function($scope, $rootScope, $timeout){
    var isPaused  = false;
    var timer_daterange = $('#rickshaw-timfer-daterange').val();

    if(timer_daterange == 'custom') {
        isPaused = true;
    }
    
    $scope.when  = function( booleanExpr, trueValue, falseValue) {
        return booleanExpr ? trueValue : falseValue;
    };


    $scope.set_timer = function() {
        if (isPaused) return;
        $timeout($scope.set_timer, 15000);
        $rootScope.$broadcast("data.update");
    }
    $scope.toggleCounter = function() {
        isPaused = !isPaused;
        $scope.set_timer();
    };

    $scope.isPaused  = function() {
        return isPaused;
    };

    $timeout(function() { $scope.set_timer() }, 15000); // delay setting the timer
    
})
.controller('RickshawChartType', function($scope, $rootScope) {

    // $scope.init = function(value){
    //     $rootScope.type  = value || 'line';
    //     $rootScope.$broadcast("set_type");
    // }
    
    

    // console.log($scope.chart_type);

    // $scope.chart_types = ['bar','line','stack'];

    // $scope.set_type = function(new_type) {
    //     $rootScope.type = new_type;
    //     $rootScope.$broadcast("set_type");
    // }

    // $scope.isActive = function(type) {
    //     if(type == $rootScope.type){
    //         return true;
    //     }
    // };
})
.directive('rickshawChart', function($window, $rootScope, $timeout, _, RickshawTimeFixtures, 
            RickshawGraphSize, Requests, Template, LoadingGlobalOptions) {
    return {
        restrict: 'E',
        scope: {},
        
        controller: ['$scope', '$element', '$attrs', 
        function($scope, $element, $attrs) {
            var data_url;
    
            $scope.$on('data.update', function() {

                var lastChar = $attrs.url.substr(-1);
                var url_separator = "&"
                if (lastChar == '/') {       
                   url_separator = '?'          
                }


                data_url = Template("{{{url}}}{{url_separator}}timestamp={{ timestamp }}", 
                    {
                    url: $attrs.url, 
                    url_separator: url_separator,
                    timestamp: $attrs.timestamp, 
                })    
                
                $scope.get_data(data_url);
            });

            $scope.get_data = function(url){

                Requests.get(url).then(function(data){
                    $scope.data = data
                    $attrs.timestamp = $scope.data.last_update;

                    // Update the current date in the dropdown and in hover
                    if(data.now_local){
                        $('#now_local').val(data.now_local);
                        $("#dropdown_now_local").text(data.now_local)
                    }
                })
            }


        }],
        link: function(scope, element, attrs) {
            var el, 
                graph, 
                hover, 
                xaxis, 
                yaxis, 
                slider,
                loading, 
                spinner, 
                timeunit, 
                series_len,
                last_element,
                data_url,
                timestamp,
                enddate;

            var w = angular.element($window);
            
            var loading_element = $(element).find('.loading').get(0);

            var element_width = RickshawGraphSize.width(element); // rickshaw-chart
            $(element).css('width', element_width.el); // rickshaw-chart
            spinner = new Spinner(LoadingGlobalOptions).spin(loading_element);
            
            // Add current value in the header
            scope.set_current_value = function() {
                var series_len = graph.series.length;
                var current_value_element = $(element).find('.charts__current');
                

                var list_element = "<li><span class='color' style='background:{{color}};'></span>{{name}}: {{value}}{{unit}}</li>";
                var unit = $(element).data('yaxis')
                
                current_value_element.empty();
                _(series_len).times(function(n){
                    var current_gauge = graph.series[n];
                    var value = _.last(current_gauge.data).y        
                    var span = Template(list_element, 
                        {"color": current_gauge.color, "name": current_gauge.name, "value": value, "unit": unit});
                    
                    current_value_element.append(span);        
                });
            }

            scope.get_window_width = function () {
                return $('body')[0].offsetWidth;
            }

            scope.get_window_height = function () {
                return $('body')[0].offsetHeight;
            }

            scope.$watch("data", function () {
                scope.update();
            });

            scope.$on("setchartsize", function () {
                scope.resize();
            });

            scope.$on("set_type", function () {
                scope.resize();
            });

            scope.$watch(scope.get_window_height, function () {
                scope.resize();
                
            });

            scope.$watch(scope.get_window_width, function () {
                scope.resize();
                
            });

            w.bind('resize', function () {
                scope.$apply();
                
            });

            scope.update = function() {
                
                if(scope.data && graph.series){

                    series_len = graph.series.length;

                    if(series_len > 0) {
                        

                        var data_length =  scope.data.data.length;
                        if(scope.data.data.length > 0){
                            
                            _(data_length).times(function(n){ 
                                var new_data = scope.data.data[n].data;
                                var graph_name = scope.data.data[n].name;

                                // Find the proper line and append the new data
                                _.each(graph.series, function(element, index){
                                        
                                    if(element.name == graph_name){
                                        var last_element_on_graph = _.last(graph.series[index].data)

                                        // Found the proper graph, go over the data
                                        _.each(new_data, function(element){
                                            if(element.x > last_element_on_graph.x) { // don't overwrite
                                                graph.series[index].data.push(element)
                                            }
                                            
                                        });


                                    graph.series[index].data.splice(0, new_data.length)

                                        
                                    }
                                
                                });    // each graph series
                                
                            }); // new data lenght
                        } // scope data length;

                        

                        // _(series_len).times(function(n){ 
                        //     _.each(scope.data.data[n].data, function(element){
                        //         if(element.x > last_element.x) { // don't overwrite
                        //             graph.series[n].data.push(element)
                        //         }
                                
                        //     });    
                            
                        //     var new_data_len = scope.data.data[n].data.length;
                        //     if(new_data_len > 0){
                        //         graph.series[n].data.splice(0, new_data_len) // remove data points from the beginning
                        //     }
                            
                            
                        // });
                            
                        last_element = _.last(graph.series[0].data)
                        
                        var first_element = _.first(graph.series[0].data)

                        // Calculate duration and update time unit
                        var duration = last_element.x-first_element.x+60;
                        timeunit = RickshawTimeFixtures.SetTimeUnit(duration);
                        xaxis.fixedTimeUnit = timeunit;    

                        // scope.set_current_value();

                    } // if series_len > 0

                    graph.render();
    

                }
                
            }, 

            scope.resize = function() {
                el = element[0]

                var element_width = RickshawGraphSize.width(el); // rickshaw-chart
                $(el).css('width', element_width.el); // rickshaw-chart
                $(el).find('.chart-slider').css('width', element_width.graph)

                if(graph) {
                    if(graph.configure) {
                            graph.configure({
                            width: element_width.graph,
                            height: 300,
                            renderer: $rootScope.type
                        });

                        timeunit = RickshawTimeFixtures.SetTimeUnit(attrs.duration);
                        xaxis.fixedTimeUnit = timeunit;
                        
                        graph.render();
                        
                    }
                    
                } else {
                    scope.render();
                }

                
            },
            scope.loading = function(data, element){
                var incoming_data = []
                if(data != undefined){
                    if (_.size(data['data']) > 0){
                        var incoming_data = data['data'].data || data['data'][0].data
                    }
                } 

                
                var size =_.size(incoming_data);

                
                spinner.stop();

                $(element).show();
                var jq_obj = $(element);
                
                if(size <=1) {
                    $(element).hide();

                    var chart_name = $(element).data('name');
                    var chart_id = $(element).attr('id');
                    $rootScope.empty_charts.push({'name': chart_name, 'id': chart_id});
                    $rootScope.$apply();
                
                }
                else {
                    $(element).find('.chart, .y_axis, .chart-slider').show();
                }
                

            },

            scope.render = function() {
                el = element[0]

                if(attrs.enddate){
                    timestamp = attrs.enddate-attrs.duration 
                } else {
                    timestamp = attrs.timestamp-attrs.duration 
                }
                
                var lastChar = attrs.url.substr(-1);
                var url_separator = "&"
                if (lastChar == '/') {       
                   url_separator = '?'          
                }

                data_url = Template("{{{url}}}{{ url_separator }}timestamp={{ timestamp }}", 
                    {    
                        url: attrs.url, 
                        url_separator: url_separator, 
                        timestamp: timestamp
                    })    

                if(attrs.enddate){
                    data_url = Template("{{{url}}}&enddate={{ enddate }}", 
                        {url: data_url, enddate: attrs.enddate})    

                }

                var element_width = RickshawGraphSize.width(el); // rickshaw-chart

                graph = new Rickshaw.Graph.Ajax({
                    element: $(el).find('.chart').get(0),
                    padding: { top: 0.2, right: 0, bottom: 0.02, left: 0 },
                    renderer: $(el).data('type') || 'line',
                    stroke: true,
                    width: element_width.graph,
                    height: 250,
                    dataURL: data_url,
                    interpolation: 'linear',
                    onData: function(d) { 
                        scope.loading(d, el);

                        return d.data
                    },
                    onComplete: function(transport) {
                        graph = transport.graph;
                        scope.set_current_value();

                        if(!hover) {
                            hover = new Rickshaw.Graph.HoverDetail({ graph: graph });
                        }
                        
                        if(!xaxis){
                            timeunit = RickshawTimeFixtures.SetTimeUnit(attrs.duration);

                            xaxis = new Rickshaw.Graph.Axis.Time({
                                graph: graph,
                                grid: true, 
                                ticks: 15,
                                timeUnit: timeunit
                            });                     
                            xaxis.render();
                        }
                        
                        if(!yaxis) {
                            yaxis = new Rickshaw.Graph.Axis.Y( {
                                graph: graph,
                                tickFormat: function(y) { return y +attrs.yaxis},
                                element: $(el).find('.y_axis').get(0),
                            });    

                            yaxis.render();
                        }

                        if(!slider) {
                            slider = new Rickshaw.Graph.RangeSlider({
                                graph: graph,
                                element: $(el).find('.chart-slider').get(0),
                            });

                        }

                        $rootScope.$apply();


                    }
                });



            }; // scope.render


        } // link

    }; // return
});