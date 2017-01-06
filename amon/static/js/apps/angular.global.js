var underscore = angular.module('underscore', []);
underscore.factory('_', function() {
    return window._;
});

var messages_list = $(".remote--messages");
function scroll_to_bottom(){
    if (messages_list.length > 0){ 
        messages_list.scrollTop(messages_list[0].scrollHeight);
    }
    
}
angular.module('BaseModule', [])
.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';    }
])
.factory('Requests', function($http){
    return {
        post: function(url, data) {
            json_data = JSON.stringify(data);
            return $http.post(url, json_data)
                .then(function(result) {
                    return result.data;
                });
        }, // post_data
        get: function(url) {
            return $http.get(url)
                .then(function(result) {
                    return result.data;
                });
        }
    } // return 
})
.factory('_', function(){
    return window._;
})
.factory('Template', function(){
    return function(template, params){
        return Mustache.render(template, params);
    }
})
.factory('Globals', function(){
     return {
            generate_uuid: function() {
                return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
                    return v.toString(16);
                });
            }
     };
})
.factory('LoadingGlobalOptions', function(){
    return {
        lines: 6, // The number of lines to draw
        length: 2, // The length of each line
        width: 3, // The line thickness
        radius: 3, // The radius of the inner circle
        corners: 1, // Corner roundness (0..1)
        rotate: 0, // The rotation offset
        direction: 1, // 1: clockwise, -1: counterclockwise
        color: '#464646', // #rgb or #rrggbb or array of colors
        speed: 3, // Rounds per second
        trail: 0, // Afterglow percentage
        shadow: false, // Whether to render a shadow
        hwaccel: true, // Whether to use hardware acceleration
        className: 'spinner', // The CSS class to assign to the spinner
        zIndex: 2e9, // The z-index (defaults to 2000000000)
        position: 'absolute',
        top: '20px', // Top position relative to parent
        left: '11px' // Left position relative to parent
    } // return
})
.service('Select2Options', function(){
    this.array = function(el){
        return {
            url: el.data('url') || false,
            size : el.data('size') || 360, 
            type: el.data('type') || false,
            placeholder: el.data('placeholder')

        }
    };
})
.directive('select2Dropdown', function(Select2Options) {
    var el;

    return {
        restrict: 'A',
        scope: {},
        priority: 1,
        link: function(scope, element, attrs) {
            el = $(element);
            var options = Select2Options.array(el); 

            el.select2({width: options.size, minimumResultsForSearch: 10, placeholder: options.placeholder});

            // Used in server Map to redirect
            if(attrs.withRedirect != undefined){
                el.on("change", function(element) {
                    
                    var redirect_url = element.val;    
                    window.location.href = redirect_url
                }) 

            } // redirect

        } // link



    }; // return
})
.directive('timeAgo', function() {
    var el;

    return {
        restrict: 'A',
        scope: {},
        priority: 1,
        link: function(scope, element, attrs) {
            el = element[0]
            var jq_obj = $(element[0]);
            var unix_timestamp = jq_obj.html();
            var moment_obj = moment.unix(unix_timestamp).fromNow();
            jq_obj.html(moment_obj)
            

        } // link

    }; // return
})
.directive('tagsDropdown', function(Select2Options, Requests, _, Template, $rootScope) {
    var el;
    return {
        restrict: 'A',
        scope: {},
        link: function(scope, element, attrs) {
            el = $(element);
            var options = Select2Options.array(el); 
            var get_all_tags_url = el.data('tags-url');

            el.select2({
                width: options.size, 
                minimumResultsForSearch: 5, 
                placeholder: options.placeholder, 
                tags: true,

                createSearchChoice: function (term) {

                    
                    if(attrs.readOnly != true){
                        if(term.length > 2){
                            return {
                                id: $.trim(term),
                                text: $.trim(term) + ' (new tag)'
                            };
                        }
                    }
                    
                    
                },
                ajax: {
                    url: get_all_tags_url,
                    dataType: 'json',
                    data: function(term, page) {
                        return {
                            q: term
                        };
                    },
                    results: function(data, page) {
                        return {

                            results: data
                        };
                    }
                },

                // Only in edit, else empty
                initSelection: function (element, callback) {
                    var selected_tags = [];
                    var tags = element.val().split(',');

                    // Get all tags, eliminate
                    Requests.get(options.url, tags).then(function(data){
                        
                        _.each(data, function(el){
                            if(_.contains(tags, el.id)){
                                
                                selected_tags.push({
                                    id: el.id,
                                    text: el.text
                                });
                            }
                        
                        });

                        callback(selected_tags);
                    })

                    

                    
                },

            
                maximumSelectionSize: 10,

                // override message for max tags
                formatSelectionTooBig: function (limit) {
                    return "Max tags is only " + limit;
                }
            


            }); //select2 end


            
            if(attrs.withRedirect != undefined){
                el.on("change", function(element) {
                    var data_url = el.data('redirect-url');
                    var tags = element.val.join(',');

                    if(tags.length > 0){
                        data_url = Template("{{{url}}}?tags={{ tags }}", 
                        {url: data_url, tags: tags,})
                    }
                    
                        
                    window.location.href = data_url
                }) 

        }

            
        

        } // link

    }; // return
})
.controller('ChatCtrl', function($scope, $attrs, Requests, $timeout, Globals, $rootScope, _){
        
    $scope.messageText = '';
    $scope.responses = []
    $scope.in_progress = []
    $scope.history = 0;
    $scope.selected_servers = [];
    $scope.servers_list;


    $scope.update_servers = function(selected_servers){
        $scope.selected_servers = selected_servers;
    }

    
    $scope.appendCommand = function(command){
        $scope.messageText = $scope.messageText + command;
    }

    $scope.sendMessage = function(keyEvent) {
        if(keyEvent){
            if (keyEvent.which != 13) return;

            if (keyEvent.which === 13) {
                keyEvent.preventDefault();
                
                var command = $scope.messageText;
            
                if(command.length == 0){
                    return;
                }
                if($scope.selected_servers.length == 0){
                    window.show_notification("Please select a server")
                    
                }

                _.each($scope.selected_servers, function(server_id) { 
                    var server_name_obj = _.findWhere($scope.servers_list, {id: server_id});
                    
                    var uuid = Globals.generate_uuid();

                    var post_data = {
                        command: command, 
                        server_id: server_id,
                        uuid: uuid
                    }

                    var task_data = {
                        host: server_name_obj.name,
                        command: command,
                        uuid: uuid
                    }


                    $scope.in_progress.push(task_data);
                    $scope.messageText = " ";
                    Requests.post($attrs.url, post_data).then(function(data){
                        $scope.responses.push(data);
                        var task_index  = _.findIndex($scope.in_progress, {uuid:uuid});
                        $scope.in_progress.splice(task_index, 1);
                    });  

                });
            }
        }
    
    }

    $scope.$watch("in_progress.length", function (value){
        $timeout(function () {
            scroll_to_bottom()
         });
        
   });

    $scope.$watch('switch', function(value) {
        $scope.switch = value;
    });


    $scope.$watch("responses.length", function (value){
        var block = $('.remote--messages');
        $timeout(function () {
            // Prism.highlightAll();
            scroll_to_bottom()
         });
        
   });

  $scope.closePanel = function(){
      $rootScope.$broadcast("close_remote_panel");
  }

   $scope.init = function(){
        Requests.get($attrs.serversurl).then(function(data){
            $scope.servers_list = _.map(data.servers, function(currentObject) {
                return _.pick(currentObject, "id", "name");
            });

            $timeout(function () {
                $rootScope.$broadcast("servers_populated");
            });

            
        }); 


   }

    $scope.$on('init_remote_panel', function (event) {
      $scope.init();
    });

              
    
})
.directive('remoteTextarea', function($window, $rootScope, _) {
    var el;

    
    var bash_words = ['ab','awk','bash','beep','cat','cc','cd','chown','chmod',
    'chroot','clear','cp','curl','cut','diff','echo','find','gawk','gcc','get',
        'git','grep','kill','killall','ln','ls','make','mkdir','mv','nc',
        'node','npm','ping','ps','restart','rm','rmdir','sed','service','sh','shopt',
        'shred','source','sort','sleep','ssh','start','stop','su','sudo','tee','telnet',
        'top','touch','vi','vim','wall','wc','wget','who','write','yes', 'apt-get', 'install',
        'version', 'yum', 'apt-add', 'remove', 'upgrade', 'status', 'service', 'systemctl',
        'home', 'var', 'etc', 'ifconfig', 'gem', 'pip', 'proc', 'uname', 'python', '--version'
    ];
    return {
        restrict: 'A',
        scope: {},
        controller: ['$scope', '$element', '$attrs',
        function($scope, $element, $attrs) {

            
        }],
        link: function(scope, element, attrs) {
            el = $(element);
            $(el).textcomplete([{
                    match: /(^|\s)(\w{2,})$/,
                    search: function (term, callback) {
                        callback($.map(bash_words, function (word) {
                            return word.indexOf(term) === 0 ? word : null;
                        }));
                    },
                    replace: function (word) {
                        return ' ' + word + ' ';
                    }
                }],  { maxCount: 20, debounce: 500, zIndex: 10001});



        }, // link

    }; // return
})
.directive('remoteserverDropdown', function(Select2Options, Requests, _) {
    var el;
    return {
        restrict: 'A',

        scope: {},
        controller: ['$scope', '$element', '$attrs',
        function($scope, $element, $attrs) {

            $scope.$on('clear_servers', function() {
                el.val('').change();
            });    


            $scope.$on('servers_populated', function() {
            
                var options = Select2Options.array(el)
                el.select2({width: options.size, minimumResultsForSearch: 5, placeholder: options.placeholder});
    
            });    

        
            
        }],
        link: function(scope, element, attrs) {
            el = $(element);

            el.on('change', function(event) {
                var value = el.val();
                scope.$parent.update_servers(value);
            });
            

        } // link

    }; // return
})
.directive('remoteTrigger', function($rootScope, $timeout) {
    var el;
    return {
        restrict: 'A',

        scope: {},
        controller: ['$scope', '$element', '$attrs',
        function($scope, $element, $attrs) {
        }],
        link: function(scope, element, attrs) {
            scope.remote_panel = false;

            scope.$on("close_remote_panel", function () {
                scope.remote_panel = false;
                $('.remote_commands--sidebar').removeClass('shown');
            });
            
     
            element.on('click', function(e){
                e.preventDefault();
                scope.remote_panel = scope.remote_panel === false ? true: false;

                if(scope.remote_panel == true){
                    
                    $rootScope.$broadcast("init_remote_panel");
                    $('.remote_commands--sidebar').addClass('shown');
                    scroll_to_bottom();
                }
                else{
                    $('.remote_commands--sidebar').removeClass('shown');
                }
            
                
                
            });
            
        

        } // link

    }; // return

})
.directive('notificationsDropdown', function(Select2Options, Template) {
    var el;

    return {
        restrict: 'A',
        scope: {},
        priority: 1,
        link: function(scope, element, attrs) {
            el = $(element);
            var options = Select2Options.array(el); 

            function format(state) {
                var originalOption = state.element;
                var image = $(originalOption).data('image')

                var template =  Template("<img style='width:24px; position:relative; top:8px; left:0px;' src='{{ image }}'/>{{text}}",
                    {image: image, text: state.text});

                return template;
            }

            function formatSelection(state) {
                var originalOption = state.element;
                var image = $(originalOption).data('image')

var template =  Template("<img style='width:24px;float:left; margin-right:10px;' src='{{ image }}'/><span style='float:left;margin-top:4px;'>{{text}}</span>",
                    {image: image, text: state.text});

                return template;
            }

            el.select2({width: options.size, minimumResultsForSearch: 10, placeholder: options.placeholder,
             formatResult: format,
             formatSelection: formatSelection,
            });

        } // link

    }; // return
});