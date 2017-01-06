"use strict";
angular.module('InlineEditor')
.controller('TagGroupsController', function($scope, Requests, $attrs, $controller){
    angular.extend(this, $controller('BaseEditorController', {$scope: $scope, Requests: Requests, $attrs: $attrs}));
    
    
    $scope.groups = [];

    
    $scope.createTag = function(keyEvent) {
        Requests.post($attrs.createturl, {name: $scope.newgroup}).then(function(data){
            $scope.groups.push(data.group);
            $scope.newgroup = '';
        }); 

    }

    $scope.deleteTag = function(tag, index) {
        var post_data = {id: tag.id};

        Requests.post($attrs.deleteurl, post_data).then(function(data){
            $scope.closeDialog(tag.id);
            $scope.groups.splice(index, 1);
        }); 
    }

    $scope.updateTag = function(tag) {        
        var post_data = {
            name: tag.name,
            id: tag.id
        }
        Requests.post($attrs.updateurl, post_data).then(function(data){
            $scope.closeDialog(tag.id)
        }); 
    }


    $scope.init = function(){
        Requests.get($attrs.list).then(function(data){
                $scope.groups = data.groups;
            
        }); 
   }

    $scope.init();
    
})