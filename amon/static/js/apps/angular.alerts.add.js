"use strict";
angular.module('AlertsAddApp', ['underscore', 'BaseModule'])
.controller('AlertsCtrl', function($scope, $attrs, Requests, LoadingGlobalOptions){
    $scope.server_metrics = []; 
    $scope.show_server_metrics = true;
    $scope.show_metrics = false;

    $scope.show_metric_types = false;
    $scope.show_tags = false;
    $scope.show_execute = false;
    $scope.metric_types = ["%"];

    $scope.show_is = false;
    $scope.show_for = false;

    $scope.update = function(value, url) {

        var post_data = {server_id: value}
        
        Requests.post(url, post_data).then(function(data){
            $scope.server_metrics = data;
        });


        $scope.show_metrics = true;
        $scope.show_tags = true;
        $scope.show_execute = false;
        if (value != 'all') {
            $scope.show_execute = true;
            $scope.show_tags = false;
        };
        
    }

    $scope.update_metric_types = function(metric_type) {
        $scope.show_metric_types = true;
        $scope.show_is = true;
        $scope.show_for = true;
        
        metric_type = metric_type.toLowerCase().replace(/\s/g, '');

        if(metric_type === 'memory'){
            $scope.metric_types = ["%", "MB"];
        }
        else if(metric_type === 'cpu') {
            $scope.metric_types = ["%",]

        }
        else if(metric_type === 'disk') {

            $scope.metric_types = ["%","MB","GB"]
        }
        else if(metric_type === 'down'){
            $scope.metric_types = []
            $scope.show_is = false;
        }
        else if(metric_type === 'network/inbound'){
            $scope.metric_types = ["KB/s"]
        }
        else if(metric_type === 'network/outbound'){
            $scope.metric_types = ["KB/s"]
        }
        else if(metric_type === 'notsendingdata'){
            $scope.metric_types = []
            $scope.show_is = false;
        }
        else if(metric_type === 'plugin'){
            $scope.metric_types = []
            $scope.show_is = true;
        }
        else {
            $scope.metric_types = []
            $scope.show_metric_types = false;
        }

        $scope.$apply();
        
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
                scope.$parent.update(value, options.url);
            }
            

            el.on('change', function() {
                var value = el.val();
                scope.$parent.update(value, options.url);
            });

        } // link

    }; // return
})
.directive('metricDropdown', function(Select2Options) {
    var el;
    return {
        restrict: 'A',
        scope: {
            server_metrics: "@"
        },
        link: function(scope, element, attrs) {
            el = $(element);
            var options = Select2Options.array(el); 

            
            var dropdown = el.select2({width: options.size, minimumResultsForSearch: 5, placeholder: options.placeholder});

            el.on('change', function() {
                var metric_type = dropdown.find(":selected").data("type");
                scope.$parent.update_metric_types(metric_type);
                $('#metric_type').find("option:first-child").attr("selected", "selected").trigger('change');
            
            });

        } // link

    }; // return
})