"use strict";
var metric_array, metric_dropdown, metric_value, values, json_data, tags, tags_dropdown;

angular.module('DashboardApp', ['underscore', 'BaseModule','RickshawApp'])
.controller('DashboardCtrl', function($scope, $attrs, Requests, LoadingGlobalOptions){

    
    var loading_target = $('.loading').get(0);
    var loading = new Spinner(LoadingGlobalOptions);

    $scope.placeholder = 'Untitled Dashboard'
    if($attrs.name){ $scope.name = $attrs.name }
    
    if($attrs.shared){ 
        $scope.shared = ($attrs.shared == 'true') ? true : false; 
    }

    $scope.UpdateName = function(value) {
        
        loading.spin(loading_target);

        var post_data = {name: value}

        Requests.post($attrs.updateurl, post_data).then(function(data){
            loading.stop();
        });  
    }

    $scope.UpdateShared = function(value) {
        
        loading.spin(loading_target);

        var post_data = {shared: value}

        Requests.post($attrs.updateurl, post_data).then(function(data){
            loading.stop();
        });  
    }


})
.controller('DashboardMetricsCtrl', function($scope, $rootScope, $attrs, Requests){
    $scope.metrics = []; 

    $scope.update = function(){
        $rootScope.empty_charts = [];
        
        Requests.get($attrs.geturl).then(function(data){
            $scope.metrics = data.data;
            $rootScope.charts_on_page = $scope.metrics.length;
            $rootScope.$broadcast("resize_charts");
        });

    }, 

    $scope.RemoveMetric = function(metric_id) {
        var post_data = {metric_id: metric_id}
        if (window.confirm("Are you sure you want to remove this metric?")) { 
            Requests.post($attrs.removeurl, post_data).then(function(data){
                $scope.update()
            });
        }
    
    },

    $scope.AddMetric = function() {
        values = new Array();
        metric_value = metric_dropdown.select2('val')
        tags_dropdown = $('#tags_dropdown');
            
        
        if(metric_value && $rootScope.metric_type == 'Server') { 
            var metric_data  = _.chain(metric_value.split('.'))
                .map(function(item) { if (item) return item.split(':'); })
                .compact()
                .object()
                .value();

            
            tags = tags_dropdown.select2('val');
            if(tags.length > 0){
                metric_data.tags = tags;
            }

            Requests.post($attrs.addurl, metric_data).then(function(data){
                $scope.update()
            });

        } 
        else if($rootScope.metric_type == 'App'){
            var app_metric_id = $("#app_metric_type").select2('val')
            

            if(app_metric_id){
                Requests.post($attrs.addurl, {'metric_id': app_metric_id, 'check': 'metric'}).then(function(data){
                    $scope.update()
                });
            }
            
        }
        else if($rootScope.metric_type == 'HealthChecks'){
            var metric_id = $("#healthcheck").select2('val')
            

            if(metric_id){
                Requests.post($attrs.addurl, {'healthcheck_id': metric_id, 'check': 'healthcheck', 'metric_type': 'healthcheck'}).then(function(data){
                    $scope.update()
                });
            }
            
        }

    
    };

    $scope.update();
    
})
.controller('DashboardMetricTypesCtrl', function($scope, $rootScope, $attrs, LoadingGlobalOptions){

    $scope.chart_types = ['Server','HealthChecks'];
    $rootScope.metric_type  = 'Server';

    $scope.set_type = function(new_type) {
        $rootScope.metric_type=new_type;
        
        $rootScope.$broadcast("set_metric_type");
    }

    $scope.isActive = function(type) {
        if(type == $rootScope.metric_type){
            return true;
        }
    };



})
.controller('DashboardServerMetricsCtrl', function($scope, $rootScope, $attrs, Requests, LoadingGlobalOptions){
    $scope.show = false;
    $scope.nodata = true;
    $scope.show_tags = false;    
    

    $scope.LoadServerMetrics = function (server_id, url) {

        if(server_id == 'all'){
            $scope.show_tags = true;
        }
        else {
            $scope.show_tags = false;
        }

        var target = $('.loading-metrics').get(0)
        var loading = new Spinner(LoadingGlobalOptions).spin(target);

        var post_data = {server_id: server_id}
        Requests.post(url, post_data).then(function(data){

            var options_array = []
            _.each(data.data, function(array){
                var s = _.object(['value', 'label','type'], array);
                options_array.push(s);

            }); 
            
            $scope.server_metrics = options_array;

            
            $scope.nodata = false;
            $scope.show = true;
            loading.stop();
        
        });
    };

    $scope.SetMetricType = function(){
        if($rootScope.metric_type == 'App'){
            $scope.show_server_metrics = false;
            $scope.show_app_metrics = true;
            $scope.show_healthchecks = false;
        }
        else if($rootScope.metric_type == 'HealthChecks'){
            $scope.show_server_metrics = false;
            $scope.show_app_metrics = false;
            $scope.show_healthchecks = true;
        }else {
            $scope.show_server_metrics = true;
            $scope.show_app_metrics = false;
            $scope.show_healthchecks = false;
        }
    }

    $scope.$on('set_metric_type', function () {
        $scope.SetMetricType();
        
    });

    $scope.SetMetricType();

})
.directive('serverDropdown', function($window, $rootScope) {
    var el;

    return {
        restrict: 'A',
        scope: {},
        controller: ['$scope', '$element', '$attrs',
        function($scope, $element, $attrs) {
            
        }],
        link: function(scope, element, attrs) {
            el = $(element);
            var url = el.data('url');
            var placeholder = el.data('placeholder')
            el.select2({width: "300", minimumResultsForSearch: 5, placeholder: placeholder});

            el.on('change', function() {
                var value = el.val();
                scope.$parent.LoadServerMetrics(value, url);
                $rootScope.$broadcast("resize_charts");
            });

            el.on("select2-open", function() { $rootScope.$broadcast("resize_charts"); })

        } // link

    }; // return
})
.directive('servermetricDropdown', function($window, $rootScope) {
    return {
        restrict: 'A',
        scope: {
            server_metrics: "@"
        },
        controller: ['$scope', '$element', '$attrs',
        function($scope, $element, $attrs) {
            
        }],
        link: function(scope, element, attrs) {
            metric_dropdown = $(element);
            var placeholder = metric_dropdown.data('placeholder')
            metric_dropdown.select2({
                width: "300", 
                minimumResultsForSearch: 5, 
                placeholder: placeholder,
            });

            metric_dropdown.select2("enable", true);

            metric_dropdown.on("select2-open", function() { $rootScope.$broadcast("resize_charts"); })


        } // link

    }; // return
})
