import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const SystemMapVisualization = ({ parts, relationships }) => {
  const svgRef = useRef(null);

  useEffect(() => {
    if (!parts.length) return;

    // Clear previous visualization
    d3.select(svgRef.current).selectAll("*").remove();

    // Setup
    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height);

    // Create force simulation
    const simulation = d3.forceSimulation(parts)
      .force("link", d3.forceLink(relationships)
        .id(d => d.id)
        .distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(50));

    // Create arrow marker for relationship lines
    svg.append("defs").selectAll("marker")
      .data(["arrow"])
      .enter().append("marker")
      .attr("id", d => d)
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 25)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#999");

    // Draw relationships
    const links = svg.append("g")
      .selectAll("line")
      .data(relationships)
      .enter().append("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 2)
      .attr("marker-end", "url(#arrow)");

    // Create node groups
    const nodes = svg.append("g")
      .selectAll("g")
      .data(parts)
      .enter().append("g")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Add circles for nodes
    nodes.append("circle")
      .attr("r", 20)
      .attr("fill", d => getColorForRole(d.role));

    // Add labels
    nodes.append("text")
      .text(d => d.name)
      .attr("text-anchor", "middle")
      .attr("dy", 30)
      .attr("fill", "#000")
      .style("font-size", "12px");

    // Add relationship labels
    svg.append("g")
      .selectAll("text")
      .data(relationships)
      .enter().append("text")
      .attr("text-anchor", "middle")
      .attr("dy", -5)
      .text(d => d.relationship_type)
      .style("font-size", "10px")
      .style("fill", "#666");

    // Update positions on each tick
    simulation.on("tick", () => {
      links
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      nodes.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    // Cleanup
    return () => {
      simulation.stop();
    };
  }, [parts, relationships]);

  // Helper function to assign colors based on role
  const getColorForRole = (role) => {
    const roleColors = {
      'protector': '#ff7f0e',
      'exile': '#1f77b4',
      'manager': '#2ca02c',
      'firefighter': '#d62728',
      'self': '#9467bd',
      'default': '#7f7f7f'
    };
    return roleColors[role?.toLowerCase()] || roleColors.default;
  };

  return (
    <svg 
      ref={svgRef} 
      style={{ width: '100%', height: '100%' }}
    />
  );
};

export default SystemMapVisualization; 