"use strict";
angular.module('RickshawApp')
.controller('CounterTimer', function($scope, $rootScope, $timeout){
    
    $scope.set_timer = function() {
        $timeout($scope.set_timer, 15000);
        $rootScope.$broadcast("update_count");
    }

    $timeout(function() { $scope.set_timer() }, 3000); // delay setting the timer
    
})
.directive('counterBlock', function($window, Requests, $timeout, $rootScope) {
    var el;

    return {
        restrict: 'E',
        scope: {},
        controller: ['$scope', '$element', '$attrs',
        function($scope, $element, $attrs) {


            $scope.update = function(){
                var url = $element.data('url');
                
                Requests.get(url).then(function(data){
                    $scope.data = data        
                })
            }

            $scope.$on('update_count', function() {
                $scope.update();
            });

            
        }],
        link: function(scope, element, attrs) {            
             scope.update();

                        

        }, // link
         template: '<span class="title">{{data.name}}</span> <span class="count">{{data.count}}</span>'
    }; // return
})