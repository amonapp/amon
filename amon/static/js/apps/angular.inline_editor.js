"use strict";
angular.module('InlineEditor', ['underscore', 'BaseModule'])

angular.module('InlineEditor')
.controller('BaseEditorController', function($scope, Requests, $attrs) {
    
    
    $scope.openEditDialog = function(id){
        $scope.open_editor = id;
        $scope.open_dialog = id;
    }
    $scope.closeDialog = function(id){
        $scope.open_editor = false;
        $scope.open_dialog = false;
        $scope.open_delete = false;
    }
    $scope.openDeleteDialog = function(id){
        $scope.open_delete = id;
        $scope.open_dialog = id;
    }


})