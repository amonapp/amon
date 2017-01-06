"use strict";
angular.module('InlineEditor')
.controller('TagsController', function($scope, Requests, $attrs, $controller){
    angular.extend(this, $controller('BaseEditorController', {$scope: $scope, Requests: Requests, $attrs: $attrs}));
    
    
    $scope.tags = [];
    $scope.tag_groups = [];

    $scope.createTag = function() {
        var post_data = {
            name: $scope.newtag.name, 
            group: $scope.newtag.group
        }
        
        Requests.post($attrs.createturl, post_data).then(function(data){
            $scope.tags.push(data.tag)
            $scope.newtag = '';
        }); 

    }

    $scope.deleteTag = function(tag, index) {
        var post_data = {id: tag.id};

        Requests.post($attrs.deleteurl, post_data).then(function(data){
            $scope.closeDialog(tag.id);
            $scope.tags.splice(index, 1);
        }); 
    }

    $scope.updateTag = function(tag) {        
        var post_data = {
            name: tag.name,
            id: tag.id,
            group: tag.group
        }
        Requests.post($attrs.updateurl, post_data).then(function(data){
            $scope.closeDialog(tag.id)
        }); 
    }


    $scope.init = function(){
        Requests.get($attrs.list).then(function(data){
            $scope.tags = data.tags;
        }); 

        Requests.get($attrs.listgroups).then(function(data){
            $scope.tag_groups = data.groups;
        }); 
   }

    $scope.init();
    
})
.directive('groupsDropdown', function(Select2Options, $timeout) {
    var el;
    return {
        require: 'ngModel',
        priority: 1,
        restrict: 'A',
        scope: {},
        controller: ['$scope', '$element', '$attrs',
        function($scope, $element, $attrs) {
        }],

        link: function(scope, element, attrs, ngModel) {
            el = $(element);

            var options = Select2Options.array(el); 
            el.select2({width: options.size, minimumResultsForSearch:15, placeholder: options.placeholder});
                    

        } // link

    }; // return
});
