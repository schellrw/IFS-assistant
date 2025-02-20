import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { 
  Tooltip, 
  Dialog, 
  DialogTitle, 
  DialogContent,
  DialogActions,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Box,
  Typography
} from '@mui/material';

const RELATIONSHIP_TYPES = [
  'protects',
  'triggered by',
  'blends with',
  'conflicts with',
  'supports',
  'manages'
];

const SystemMapVisualization = ({ 
  parts, 
  relationships,
  onAddRelationship,
  onUpdateRelationship,
  onDeleteRelationship 
}) => {
  const svgRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [relationshipDialog, setRelationshipDialog] = useState({
    open: false,
    source: null,
    target: null,
    type: '',
    description: ''
  });

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
      .attr("marker-end", "url(#arrow)")
      .on("mouseover", (event, d) => {
        d3.select(event.target)
          .attr("stroke-width", 4)
          .attr("stroke", "#666");
      })
      .on("mouseout", (event) => {
        d3.select(event.target)
          .attr("stroke-width", 2)
          .attr("stroke", "#999");
      })
      .on("click", (event, d) => {
        // Edit relationship
        setRelationshipDialog({
          open: true,
          source: d.source,
          target: d.target,
          type: d.relationship_type,
          description: d.description,
          existing: d
        });
      });

    // Create node groups
    const nodes = svg.append("g")
      .selectAll("g")
      .data(parts)
      .enter().append("g")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))
      .on("mouseover", (event, d) => {
        setSelectedNode(d);
        
        // Show tooltip
        const tooltip = d3.select("#node-tooltip")
          .style("visibility", "visible")
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 10) + "px");
        
        tooltip.select(".name").text(d.name);
        tooltip.select(".role").text(d.role || "No role");
        tooltip.select(".description").text(d.description || "No description");
      })
      .on("mouseout", () => {
        setSelectedNode(null);
        d3.select("#node-tooltip").style("visibility", "hidden");
      })
      .on("click", (event, d) => {
        if (event.ctrlKey || event.metaKey) {
          // Start relationship creation
          if (!relationshipDialog.source) {
            setRelationshipDialog(prev => ({
              ...prev,
              source: d
            }));
          } else if (relationshipDialog.source.id !== d.id) {
            setRelationshipDialog(prev => ({
              ...prev,
              open: true,
              target: d,
              type: '',
              description: ''
            }));
          }
        }
      });

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

  const handleRelationshipSave = () => {
    const { source, target, type, description, existing } = relationshipDialog;
    
    if (existing) {
      // Update existing relationship
      onUpdateRelationship(existing.id, {
        relationship_type: type,
        description
      });
    } else {
      // Create new relationship
      onAddRelationship({
        source_id: source.id,
        target_id: target.id,
        relationship_type: type,
        description
      });
    }
    
    handleDialogClose();
  };

  const handleDialogClose = () => {
    setRelationshipDialog({
      open: false,
      source: null,
      target: null,
      type: '',
      description: ''
    });
  };

  return (
    <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
      <svg 
        ref={svgRef} 
        style={{ width: '100%', height: '100%' }}
      />
      
      {/* Tooltip */}
      <div
        id="node-tooltip"
        style={{
          position: 'absolute',
          visibility: 'hidden',
          backgroundColor: 'white',
          border: '1px solid #ccc',
          borderRadius: '4px',
          padding: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
          zIndex: 1000
        }}
      >
        <div className="name" style={{ fontWeight: 'bold' }}></div>
        <div className="role" style={{ color: '#666' }}></div>
        <div className="description" style={{ fontSize: '0.9em' }}></div>
      </div>

      {/* Relationship Dialog */}
      <Dialog 
        open={relationshipDialog.open} 
        onClose={handleDialogClose}
      >
        <DialogTitle>
          {relationshipDialog.existing ? 'Edit Relationship' : 'Create Relationship'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Relationship Type</InputLabel>
              <Select
                value={relationshipDialog.type}
                onChange={(e) => setRelationshipDialog(prev => ({
                  ...prev,
                  type: e.target.value
                }))}
              >
                {RELATIONSHIP_TYPES.map(type => (
                  <MenuItem key={type} value={type}>
                    {type}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Description"
              value={relationshipDialog.description}
              onChange={(e) => setRelationshipDialog(prev => ({
                ...prev,
                description: e.target.value
              }))}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          {relationshipDialog.existing && (
            <Button 
              color="error" 
              onClick={() => {
                onDeleteRelationship(relationshipDialog.existing.id);
                handleDialogClose();
              }}
            >
              Delete
            </Button>
          )}
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button onClick={handleRelationshipSave} variant="contained">
            {relationshipDialog.existing ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Instructions */}
      {selectedNode === null && (
        <Box
          sx={{
            position: 'absolute',
            bottom: 16,
            left: 16,
            backgroundColor: 'rgba(255,255,255,0.9)',
            padding: 2,
            borderRadius: 1,
            boxShadow: 1
          }}
        >
          <Typography variant="body2">
            • Click and drag nodes to move them
            <br />
            • Ctrl/Cmd + Click two nodes to create a relationship
            <br />
            • Click a relationship line to edit it
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default SystemMapVisualization; 