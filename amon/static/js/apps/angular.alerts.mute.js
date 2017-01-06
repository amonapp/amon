"use strict";
angular.module('AlertsMuteApp', ['underscore', 'BaseModule'])
.controller('AlertsMuteCtrl', function($scope, $attrs, LoadingGlobalOptions){

    $scope.show_tags = true;

    $scope.update = function(server_id){
        $scope.show_tags = false;
        if (server_id == 'all') {
            $scope.show_tags = true;
        };

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

            el.select2({width: options.size, minimumResultsForSearch: 10, placeholder: options.placeholder});

            
            el.on('change', function(event) {
                var value = el.val();
                scope.$parent.update(value);
            });
        

        } // link

    }; // return
})