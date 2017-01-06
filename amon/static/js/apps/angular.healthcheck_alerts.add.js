"use strict";
angular.module('HealthCheckAddAlertApp', ['underscore', 'BaseModule'])
.controller('HealthCheckAlertsCtrl', function($scope, $attrs, Requests, LoadingGlobalOptions){
    $scope.commands = []; 
    $scope.params = []

    $scope.show_commands = false;
    $scope.show_params = false;
    $scope.show_tags = false;
    $scope.show_status = false;
    $scope.show_for = false;

    $scope.update_servers = function(value, url) {
        var post_data = {server_id: value}
        $scope.commands = []
        $scope.params = []
        
        Requests.post(url, post_data).then(function(data){
            $scope.commands = data;
        });

        $scope.show_status = true;
        $scope.show_commands = true;
        $scope.show_for = true;
        $scope.show_params = true;
        $scope.show_tags = true;

        if (value != 'all') {
            $scope.show_tags = false;
            $scope.show_params = false;
        };
        
    }


    $scope.update_params = function(value, url) {
        $scope.params = []
        var post_data = {command: value}
        
        Requests.post(url, post_data).then(function(data){
            $scope.params = data;
        });
        
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
                scope.$parent.update_servers(value, options.url);
            }
            

            el.on('change', function() {
                var value = el.val();
                scope.$parent.update_servers(value, options.url);
            });

        } // link

    }; // return
})
.directive('commandDropdown', function(Select2Options) {
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

            var value = el.val();
            if(value) {
                scope.$parent.update_params(value, options.url);
            }
            

            el.on('change', function() {
                var value = el.val();
                scope.$parent.update_params(value, options.url);
            });

        } // link

    }; // return
})