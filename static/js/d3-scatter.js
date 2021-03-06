/* Example based on http://bl.ocks.org/mbostock/3887118 */
/* Tooltip example from
 * http://www.d3noob.org/2013/01/adding-tooltips-to-d3js-graph.html */


function plot_scatter_d3(plotid, plot_parms)
{
    var divname = 'plot' + plotid;
    var divtag = '#' + divname;
    var $mydiv = $(divtag);
    var divht = $('#plotwin').height();
    var margin = {top: 20, right: 20, bottom: 30, left: 40},
        width = $mydiv.parent().width() - margin.left - margin.right,
        height = $mydiv.parent().height() - margin.top - margin.bottom;

//    plot_parms['xfield'] = "ELAPSED_USECS.D";
//    plot_parms['yfields'] = "LBA.I";
    /* 
    * value accessor - returns the value to encode for a given data object.
    * scale - maps value to a visual display encoding, such as a pixel position.
    * map function - maps from data value to display value
    * axis - sets up axis
    */ 

    // setup x 
    var xValue = function(d) { return d[plot_parms['xfield']];}, // data -> value
        xScale = d3.scale.linear().range([0, width]), // value -> display
        xMap = function(d) { return xScale(xValue(d));}, // data -> display
        xAxis = d3.svg.axis().scale(xScale).orient("bottom");

    // setup y
    var yValue = function(d) { return d[plot_parms['yfields']];}, // data -> value
        yScale = d3.scale.linear().range([height, 0]), // value -> display
        yMap = function(d) { return yScale(yValue(d));}, // data -> display
        yAxis = d3.svg.axis().scale(yScale).orient("left");

    // setup fill color
    var cValue = function(d) { return 0;},
        color = d3.scale.category10();

    // add the graph canvas to the body of the webpage
    var svg = d3.select(divtag).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
    .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // add the tooltip area to the webpage
    var tooltip = d3.select(divtag).append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    // load data
    var csv_url = "/getdata?" + serialize(plot_parms) + '&name=plot' + plotid;
    d3.csv(csv_url, function(error, data) {
        var newkeys = {};
        for (var key in data[0]) {
            var newkey = key.replace(/^#?(.*)\.[SDI]$/gi, "$1");
            if (newkey != key) {
                newkeys[key] = newkey;
            }

        }
        data.forEach(function(d) {
            for (var key in d)
                d[newkeys[key]] = +d[key];
        });
        $('.hourglass').hide();

        // don't want dots overlapping axis, so add in buffer to data domain
        xScale.domain([d3.min(data, xValue)-1, d3.max(data, xValue)+1]);
        yScale.domain([d3.min(data, yValue)-1, d3.max(data, yValue)+1]);

        // x-axis
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis)
            .append("text")
            .attr("class", "label")
            .attr("x", width)
            .attr("y", -6)
            .style("text-anchor", "end")
            .text(plot_parms['xfield']);

        // y-axis
        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)
            .append("text")
            .attr("class", "label")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text(plot_parms['yfields']);

        // draw dots
        svg.selectAll(".dot")
            .data(data)
            .enter().append("circle")
            .attr("class", "dot")
            .attr("r", 1)
            .attr("cx", xMap)
            .attr("cy", yMap)
            .style("fill", function(d) { return color(cValue(d));}) 
            .on("mouseover", function(d) {
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                tooltip.html(plot_parms['xfield'] + " = " + xValue(d) 
                    + "<br>" + plot_parms['yfields'] + " = " + yValue(d))
                    .style("left", (d3.event.pageX + 5) + "px")
                    .style("top", (d3.event.pageY - 28) + "px");
            })
            .on("mouseout", function(d) {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            });

        // draw legend
        var legend = svg.selectAll(".legend")
            .data(color.domain())
            .enter().append("g")
            .attr("class", "legend")
            .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

        // draw legend colored rectangles
        legend.append("rect")
            .attr("x", width - 18)
            .attr("width", 18)
            .attr("height", 18)
            .style("fill", color);

        // draw legend text
        legend.append("text")
            .attr("x", width - 24)
            .attr("y", 9)
            .attr("dy", ".35em")
            .style("text-anchor", "end")
            .text(function(d) { return d;})
    });
}
