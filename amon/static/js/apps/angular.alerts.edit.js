"use strict";
angular.module('AlertsEditApp', ['underscore', 'BaseModule'])
.controller('AlertsCtrl', function($scope, $attrs, Requests, LoadingGlobalOptions){
    $scope.server_metrics = []; 
    $scope.show_server_metrics = true;

    $scope.show_metric_types = true;
    $scope.show_is = true;
    $scope.show_tags = true;
    $scope.show_execute = false;




    $scope.update = function(server_id){
        if (server_id != 'all') {
            $scope.show_execute = true;
            $scope.show_tags = false;
        }
    }

    $scope.update_metric_types = function(metric_type) {

        $scope.show_metric_types = true;
        $scope.show_is = true;
        metric_type = metric_type.toLowerCase();

        if(metric_type === 'down'){
            $scope.show_is = false;
        }
        else if(metric_type === 'loadavg') {
            $scope.show_metric_types = false;
        }
        else if(metric_type == 'notsendingdata'){
            $scope.show_is = false;
        }        
        
    }

    
})
.directive('serverDropdown', function(Select2Options) {
    var el;
    return {
        restrict: 'A',
        scope: {},
        link: function(scope, element, attrs) {
            el = $(element);
            var options = Select2Options.array(el); 

            el.select2({width: options.size, minimumResultsForSearch: 5, placeholder: options.placeholder});

            var value = el.val();
            if(value) {
                scope.$parent.update(value);
            }

            el.select2('disable')
        

        } // link

    }; // return
})
.directive('metricDropdown', function(Select2Options) {
    var el;
    return {
        restrict: 'A',
         priority: 1,
        scope: {
            server_metrics: "@"
        },
        link: function(scope, element, attrs) {
            el = $(element);
            var options = Select2Options.array(el); 
            var selected_value = el.data('selected');
            var metric_type = el.data('type') || '';

            scope.$parent.update_metric_types(metric_type);
            var dropdown = el.select2({width: options.size, minimumResultsForSearch: 5, placeholder: options.placeholder});

            dropdown.val(selected_value).trigger('change')
            dropdown.select2('disable');

            

        } // link

    }; // return
})