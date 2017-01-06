Rickshaw.namespace('Rickshaw.Graph.HoverDetail');

function formatSizeUnits(bytes){
      if      (bytes>=1073741824) {bytes=(bytes/1073741824).toFixed(2)+' GB';}
      else if (bytes>=1048576)    {bytes=(bytes/1048576).toFixed(2)+' MB';}
      else if (bytes>=1024)       {bytes=(bytes/1024).toFixed(2)+' KB';}
      else if (bytes>1)           {bytes=bytes+' bytes';}
      else if (bytes==1)          {bytes=bytes+' byte';}
      else                        {bytes='0 byte';}
      return bytes;
}

function render_underscore_template(template, params){
    _.templateSettings = {interpolate : /\{\{(.+?)\}\}/g};

    var render = _.template(template)

    return render(params)
    
}

Rickshaw.Graph.HoverDetail = Rickshaw.Class.create({

    initialize: function(args) {
        
        var graph = this.graph = args.graph;

        this.xFormatter = args.xFormatter || function(x) {
            return new Date( x * 1000 ).toUTCString();
        };

        this.yFormatter = args.yFormatter || function(y) {
            return y === null ? y : y.toFixed(2);
        };

        var element = this.element = document.createElement('div');
        element.className = 'detail';

        this.visible = true;
        graph.element.appendChild(element);

        this.lastEvent = null;
        this._addListeners();

        this.onShow = args.onShow;
        this.onHide = args.onHide;
        this.onRender = args.onRender;

        this.formatter = args.formatter || this.formatter;

    },

    formatter: function(series, x, y, formattedX, formattedY, d) {
        return series.name + ':&nbsp;' + formattedY;
    },

    update: function(e) {

        e = e || this.lastEvent;
        if (!e) return;
        this.lastEvent = e;

        if (!e.target.nodeName.match(/^(path|svg|rect|circle)$/)) return;

        var graph = this.graph;

        var eventX = e.offsetX || e.layerX;
        var eventY = e.offsetY || e.layerY;

        var j = 0;
        var points = [];
        var nearestPoint;

        this.graph.series.active().forEach( function(series) {

            var data = this.graph.stackedData[j++];

            if (!data.length)
                return;

            var domainX = graph.x.invert(eventX);

            var domainIndexScale = d3.scale.linear()
                .domain([data[0].x, data.slice(-1)[0].x])
                .range([0, data.length - 1]);

            var approximateIndex = Math.round(domainIndexScale(domainX));
            if (approximateIndex == data.length - 1) approximateIndex--;

            var dataIndex = Math.min(approximateIndex || 0, data.length - 1);

            for (var i = approximateIndex; i < data.length - 1;) {

                if (!data[i] || !data[i + 1]) break;

                if (data[i].x <= domainX && data[i + 1].x > domainX) {
                    dataIndex = Math.abs(domainX - data[i].x) < Math.abs(domainX - data[i + 1].x) ? i : i + 1;
                    break;
                }

                if (data[i + 1].x <= domainX) { i++ } else { i-- }
            }

            if (dataIndex < 0) dataIndex = 0;
            var value = data[dataIndex];

            var distance = Math.sqrt(
                Math.pow(Math.abs(graph.x(value.x) - eventX), 2) +
                Math.pow(Math.abs(graph.y(value.y + value.y0) - eventY), 2)
            );
            

            var xFormatter = series.xFormatter || this.xFormatter;
            var yFormatter = series.yFormatter || this.yFormatter;

            var point = {
                formattedXValue: xFormatter(value.x),
                formattedYValue: yFormatter(series.scale ? series.scale.invert(value.y) : value.y),
                series: series,
                value: value,
                distance: distance,
                order: j,
                name: series.name
            };

            if (!nearestPoint || distance < nearestPoint.distance) {
                nearestPoint = point;
            }

            points.push(point);

        }, this );

        if (!nearestPoint)
            return;

        nearestPoint.active = true;

        var domainX = nearestPoint.value.x;
        var formattedXValue = nearestPoint.formattedXValue;

        this.element.innerHTML = '';
        this.element.style.left = graph.x(domainX) + 'px';

        this.visible && this.render( {
            points: points,
            detail: points, // for backwards compatibility
            mouseX: eventX,
            mouseY: eventY,
            formattedXValue: formattedXValue,
            domainX: domainX
        } );
    },

    hide: function() {
        this.visible = false;
        this.element.classList.add('inactive');

        if (typeof this.onHide == 'function') {
            this.onHide();
        }
    },

    show: function() {
        this.visible = true;
        this.element.classList.remove('inactive');

        if (typeof this.onShow == 'function') {
            this.onShow();
        }
    },

    render: function(args) {

        var graph = this.graph;
        var points = args.points;
        var point = points.filter( function(p) { return p.active } ).shift();

        if (point.value.y === null) return;

        var formattedXValue = point.formattedXValue;
        var formattedYValue = point.formattedYValue;

        this.element.innerHTML = '';
        this.element.style.left = graph.x(point.value.x) + 'px';

        var xLabel = document.createElement('div');

        xLabel.className = 'x_label';
        xLabel.innerHTML = formattedXValue;
        this.element.appendChild(xLabel);

        var item = document.createElement('div');

        item.className = 'item';

        // invert the scale if this series displays using a scale
        var series = point.series;
        var actualY = series.scale ? series.scale.invert(point.value.y) : point.value.y;


        var dot = document.createElement('div');

        dot.className = 'dot';
        dot.style.top = item.style.top;
        dot.style.borderColor = series.color;

        // tooltip fix
        if (graph.width - $(item).width() <= graph.x(point.value.x)) {
            $(item).addClass('left-sided');
        };

        if (point.active) {
            $(item).addClass('active');
            dot.className = 'dot active';
        }



        metric = $(graph.element).data('yaxis');    

        // Set timestamp
        now_local = $('#now_local').val();

        if(now_local != undefined){
            now_local_utc = moment.utc(now_local, ["DD.MM.YYYY-HH:mm"]);
            timestamp_utc = moment.utc(args.formattedXValue);

        
            timestamp = moment(args.formattedXValue).utc().format("DD.MM.YYYY HH:mm:ss");
            from_now = timestamp_utc.from(now_local_utc);
            from_now = render_underscore_template("({{from_now}})", {"from_now": from_now})
        }
        else {
            from_now = '';
            timestamp = '';
        }
        
        
        time_template = render_underscore_template("{{timestamp}} {{from_now}}", {"timestamp": timestamp, "from_now": from_now})
        $('#legend_timestamp').html(time_template);

        var current_element = render_underscore_template("#{{id}}-current", {"id": $(graph.element).data('id')})
    
        var list_element = "<li><span class='color' style='background:{{color}};'></span>{{value}}</li>";
        
        list_elements = [];

        
        window.point = point;
        // Show all points on hover 
        args.detail.sort(function(a, b) { return a.order - b.order }).forEach( function(d) {
            var dot = document.createElement('div');
            dot.className = 'dot';
            dot.style.top = this.graph.y(d.value.y0 + d.value.y) + 'px';
            dot.style.borderColor = d.series.color;


            this.element.appendChild(dot);
            dot.className = 'dot active';
            
            this.show();
            legend_color = d.series.color;

            // Area charts
            if(typeof(d.series.stroke) == 'string'){
                legend_color = d.series.stroke;
            }

            var bold = ""
            if(d == window.point){
                bold = "<strong>"
            }

                    
            value = render_underscore_template("{{bold}} {{d.name}}:  {{d.value.y}}{{metric}} {{bold}}", 
                    {"d": d, "metric": metric, bold: bold});
            var point = {"value": value, "color": legend_color};
            
            rendered_list_element = render_underscore_template(list_element, point);
            list_elements.push(rendered_list_element);

        },this);


        legend_height = 60;
        

        $('#legend_list').html(list_elements);
        //$(current_element).html();
        $("#legend").show();
        
        
        this.show();

        if (typeof this.onRender == 'function') {
            this.onRender(args);
        }
    },

    _addListeners: function() {

        this.graph.element.addEventListener(
            'mousemove',
            function(e) {
                this.visible = true;
                this.update(e);
            }.bind(this),
            false
        );

        this.graph.onUpdate( function() { this.update() }.bind(this) );

        this.graph.element.addEventListener(
            'mouseout',
            function(e) {
                $("#legend").hide();
                if (e.relatedTarget && !(e.relatedTarget.compareDocumentPosition(this.graph.element) & Node.DOCUMENT_POSITION_CONTAINS)) {
                    this.hide();
                }
            }.bind(this),
            false
        );
    }
});
