"""
D3.js Visualization Components for Streamlit
Provides interactive D3-based charts as alternatives to Plotly
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json

def create_d3_bar_chart(data, x_col, y_col, title="", height=400, color="#1f77b4"):
    """Create an interactive D3.js bar chart"""
    
    chart_data = data[[x_col, y_col]].to_dict('records')
    data_json = json.dumps(chart_data)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; }}
            .chart-title {{ font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #1f2937; }}
            .bar {{ transition: all 0.3s ease; }}
            .bar:hover {{ opacity: 0.8; cursor: pointer; }}
            .tooltip {{ position: absolute; padding: 10px; background: rgba(0, 0, 0, 0.8); color: white; border-radius: 5px; pointer-events: none; font-size: 12px; opacity: 0; transition: opacity 0.3s; }}
            .axis text {{ font-size: 11px; fill: #6b7280; }}
            .axis line, .axis path {{ stroke: #e5e7eb; }}
            .grid line {{ stroke: #f3f4f6; stroke-dasharray: 2,2; }}
        </style>
    </head>
    <body>
        <div class="chart-title">{title}</div>
        <div id="chart"></div>
        <div class="tooltip" id="tooltip"></div>
        
        <script>
            const data = {data_json};
            const margin = {{top: 20, right: 30, bottom: 60, left: 70}};
            const width = 800;
            const height = {height} - margin.top - margin.bottom;
            
            const svg = d3.select("#chart").append("svg").attr("width", width).attr("height", height + margin.top + margin.bottom)
                .append("g").attr("transform", `translate(${{margin.left}},${{margin.top}})`);
            
            const x = d3.scaleBand().domain(data.map(d => d.{x_col})).range([0, width - margin.left - margin.right]).padding(0.2);
            const y = d3.scaleLinear().domain([0, d3.max(data, d => d.{y_col}) * 1.1]).nice().range([height, 0]);
            
            svg.append("g").attr("class", "grid").call(d3.axisLeft(y).tickSize(-(width - margin.left - margin.right)).tickFormat(""));
            svg.append("g").attr("class", "axis").attr("transform", `translate(0,${{height}})`).call(d3.axisBottom(x))
                .selectAll("text").attr("transform", "rotate(-45)").style("text-anchor", "end");
            svg.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(8).tickFormat(d => d3.format(",.0f")(d)));
            
            const tooltip = d3.select("#tooltip");
            
            svg.selectAll(".bar").data(data).enter().append("rect").attr("class", "bar")
                .attr("x", d => x(d.{x_col})).attr("width", x.bandwidth()).attr("y", height).attr("height", 0).attr("fill", "{color}")
                .on("mouseover", function(event, d) {{
                    d3.select(this).attr("fill", d3.color("{color}").darker(0.5));
                    tooltip.style("opacity", 1).html(`<strong>${{d.{x_col}}}</strong><br/>{y_col}: ${{d3.format(",.0f")(d.{y_col})}}`);
                }})
                .on("mousemove", function(event) {{ tooltip.style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px"); }})
                .on("mouseout", function() {{ d3.select(this).attr("fill", "{color}"); tooltip.style("opacity", 0); }})
                .transition().duration(800).delay((d, i) => i * 50).attr("y", d => y(d.{y_col})).attr("height", d => height - y(d.{y_col}));
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=height + 100, scrolling=False)


def create_d3_line_chart(data, x_col, y_col, title="", height=400, color="#2ca02c"):
    """Create an interactive D3.js line chart"""
    
    chart_data = data[[x_col, y_col]].sort_values(x_col).to_dict('records')
    data_json = json.dumps(chart_data)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; }}
            .chart-title {{ font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #1f2937; }}
            .line {{ fill: none; stroke: {color}; stroke-width: 3; }}
            .dot {{ fill: {color}; stroke: white; stroke-width: 2; cursor: pointer; }}
            .tooltip {{ position: absolute; padding: 10px; background: rgba(0, 0, 0, 0.8); color: white; border-radius: 5px; pointer-events: none; font-size: 12px; opacity: 0; }}
            .axis text {{ font-size: 11px; fill: #6b7280; }}
            .grid line {{ stroke: #f3f4f6; stroke-dasharray: 2,2; }}
        </style>
    </head>
    <body>
        <div class="chart-title">{title}</div>
        <div id="chart"></div>
        <div class="tooltip" id="tooltip"></div>
        
        <script>
            const data = {data_json};
            const margin = {{top: 20, right: 30, bottom: 60, left: 70}};
            const width = 800;
            const height = {height} - margin.top - margin.bottom;
            
            const svg = d3.select("#chart").append("svg").attr("width", width).attr("height", height + margin.top + margin.bottom)
                .append("g").attr("transform", `translate(${{margin.left}},${{margin.top}})`);
            
            const x = d3.scaleBand().domain(data.map(d => d.{x_col})).range([0, width - margin.left - margin.right]).padding(0.1);
            const y = d3.scaleLinear().domain([0, d3.max(data, d => d.{y_col}) * 1.1]).nice().range([height, 0]);
            
            svg.append("g").attr("class", "grid").call(d3.axisLeft(y).tickSize(-(width - margin.left - margin.right)).tickFormat(""));
            svg.append("g").attr("class", "axis").attr("transform", `translate(0,${{height}})`).call(d3.axisBottom(x))
                .selectAll("text").attr("transform", "rotate(-45)").style("text-anchor", "end");
            svg.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(8).tickFormat(d => d3.format(",.0f")(d)));
            
            const line = d3.line().x(d => x(d.{x_col}) + x.bandwidth() / 2).y(d => y(d.{y_col})).curve(d3.curveMonotoneX);
            
            const path = svg.append("path").datum(data).attr("class", "line").attr("d", line);
            const totalLength = path.node().getTotalLength();
            path.attr("stroke-dasharray", totalLength + " " + totalLength).attr("stroke-dashoffset", totalLength)
                .transition().duration(1500).ease(d3.easeLinear).attr("stroke-dashoffset", 0);
            
            const tooltip = d3.select("#tooltip");
            
            svg.selectAll(".dot").data(data).enter().append("circle").attr("class", "dot")
                .attr("cx", d => x(d.{x_col}) + x.bandwidth() / 2).attr("cy", d => y(d.{y_col})).attr("r", 0)
                .on("mouseover", function(event, d) {{
                    d3.select(this).attr("r", 6);
                    tooltip.style("opacity", 1).html(`<strong>${{d.{x_col}}}</strong><br/>{y_col}: ${{d3.format(",.0f")(d.{y_col})}}`);
                }})
                .on("mousemove", function(event) {{ tooltip.style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px"); }})
                .on("mouseout", function() {{ d3.select(this).attr("r", 4); tooltip.style("opacity", 0); }})
                .transition().delay(1500).duration(300).attr("r", 4);
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=height + 100, scrolling=False)


def create_d3_grouped_bar_chart(data, x_col, y_cols, labels, title="", height=400, colors=None):
    """Create an interactive D3.js grouped bar chart"""
    
    if colors is None:
        colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]
    
    chart_data = []
    for _, row in data.iterrows():
        item = {x_col: str(row[x_col])}
        for col in y_cols:
            item[col] = float(row[col]) if pd.notna(row[col]) else 0
        chart_data.append(item)
    
    data_json = json.dumps(chart_data)
    y_cols_json = json.dumps(y_cols)
    labels_json = json.dumps(labels)
    colors_json = json.dumps(colors[:len(y_cols)])
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; }}
            .chart-title {{ font-size: 18px; font-weight: 600; margin-bottom: 15px; color: #1f2937; }}
            .bar {{ transition: all 0.3s ease; }}
            .bar:hover {{ opacity: 0.8; cursor: pointer; }}
            .legend {{ font-size: 12px; margin-bottom: 15px; }}
            .legend-item {{ margin-right: 20px; display: inline-block; }}
            .legend-color {{ width: 12px; height: 12px; display: inline-block; margin-right: 5px; border-radius: 2px; }}
            .tooltip {{ position: absolute; padding: 10px; background: rgba(0, 0, 0, 0.8); color: white; border-radius: 5px; pointer-events: none; font-size: 12px; opacity: 0; }}
            .axis text {{ font-size: 11px; fill: #6b7280; }}
            .grid line {{ stroke: #f3f4f6; stroke-dasharray: 2,2; }}
        </style>
    </head>
    <body>
        <div class="chart-title">{title}</div>
        <div id="legend" class="legend"></div>
        <div id="chart"></div>
        <div class="tooltip" id="tooltip"></div>
        
        <script>
            const data = {data_json};
            const keys = {y_cols_json};
            const labels = {labels_json};
            const colors = {colors_json};
            const margin = {{top: 20, right: 30, bottom: 60, left: 70}};
            const width = 800;
            const height = {height} - margin.top - margin.bottom;
            
            const color = d3.scaleOrdinal().domain(keys).range(colors);
            
            d3.select("#legend").selectAll(".legend-item").data(keys).enter().append("span").attr("class", "legend-item")
                .html((d, i) => `<span class="legend-color" style="background-color: ${{color(d)}}"></span>${{labels[i]}}`);
            
            const svg = d3.select("#chart").append("svg").attr("width", width).attr("height", height + margin.top + margin.bottom)
                .append("g").attr("transform", `translate(${{margin.left}},${{margin.top}})`);
            
            const x0 = d3.scaleBand().domain(data.map(d => d.{x_col})).range([0, width - margin.left - margin.right]).padding(0.2);
            const x1 = d3.scaleBand().domain(keys).range([0, x0.bandwidth()]).padding(0.05);
            const y = d3.scaleLinear().domain([0, d3.max(data, d => d3.max(keys, key => d[key])) * 1.1]).nice().range([height, 0]);
            
            svg.append("g").attr("class", "grid").call(d3.axisLeft(y).tickSize(-(width - margin.left - margin.right)).tickFormat(""));
            svg.append("g").attr("class", "axis").attr("transform", `translate(0,${{height}})`).call(d3.axisBottom(x0))
                .selectAll("text").attr("transform", "rotate(-45)").style("text-anchor", "end");
            svg.append("g").attr("class", "axis").call(d3.axisLeft(y).ticks(8).tickFormat(d => d3.format(",.0f")(d)));
            
            const tooltip = d3.select("#tooltip");
            
            const barGroups = svg.selectAll(".bar-group").data(data).enter().append("g").attr("class", "bar-group")
                .attr("transform", d => `translate(${{x0(d.{x_col})}},0)`);
            
            barGroups.selectAll(".bar").data(d => keys.map(key => ({{key: key, value: d[key], category: d.{x_col}}})))
                .enter().append("rect").attr("class", "bar").attr("x", d => x1(d.key)).attr("width", x1.bandwidth())
                .attr("y", height).attr("height", 0).attr("fill", d => color(d.key))
                .on("mouseover", function(event, d) {{
                    const idx = keys.indexOf(d.key);
                    d3.select(this).attr("fill", d3.color(color(d.key)).darker(0.5));
                    tooltip.style("opacity", 1).html(`<strong>${{d.category}}</strong><br/>${{labels[idx]}}: ${{d3.format(",.0f")(d.value)}}`);
                }})
                .on("mousemove", function(event) {{ tooltip.style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px"); }})
                .on("mouseout", function(event, d) {{ d3.select(this).attr("fill", color(d.key)); tooltip.style("opacity", 0); }})
                .transition().duration(800).delay((d, i) => i * 50).attr("y", d => y(d.value)).attr("height", d => height - y(d.value));
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=height + 120, scrolling=False)
