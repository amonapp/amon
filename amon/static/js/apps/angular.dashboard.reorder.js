"use strict";

angular.module('DashboardReorderApp', ['underscore', 'BaseModule', angularDragula(angular)])
.controller('DashboardReorderCtrl', function($scope, $attrs, Requests, LoadingGlobalOptions){
    $scope.charts = []; 
    $scope.checks = [];

    $scope.init = function(){
        Requests.get($attrs.geturl).then(function(data){

            _.each(data.data, function(el){
                if (el.type == 'healthcheck') {
                    $scope.checks.push(el);
                }
                else {
                    $scope.charts.push(el);
                }
            
            }); 

        });

    }, 

    $scope.$on('charts-list.drop-model', function (el, target, source) {
        var new_order = _.pluck($scope.charts, 'id');
         var data = {
             'new_order': new_order
         }
         Requests.post($attrs.orderurl, data).then(function(data) {});
        
    });

    $scope.$on('checks-list.drop-model', function (el, target, source) {
        var new_order = _.pluck($scope.checks, 'id');
         var data = {
             'new_order': new_order
         }
         Requests.post($attrs.orderurl, data).then(function(data) {});
        
    });
    
    $scope.init();

})
