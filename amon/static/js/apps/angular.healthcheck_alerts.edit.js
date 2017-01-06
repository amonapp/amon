"use strict";
angular.module('HealthCheckEditAlertsApp', ['underscore', 'BaseModule'])
.controller('HealthCheckAlertsCtrl', function($scope, $attrs, Requests, LoadingGlobalOptions){

    $scope.show_tags = false;
    $scope.show_status = true;
    $scope.show_for = true;

    $scope.update_servers = function(value, url) {
        if (value == 'all') {
            $scope.show_tags = true;
        };
        
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
            scope.$parent.update_servers(value);

            el.select2('disable');
                        

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

            el.select2('disable');

        } // link

    }; // return
})