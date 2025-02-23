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
  Typography,
  Alert
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
  const [relationshipStart, setRelationshipStart] = useState(null);
  const [relationshipDialog, setRelationshipDialog] = useState({
    open: false,
    source: null,
    target: null,
    type: '',
    description: ''
  });

  useEffect(() => {
    if (!parts.length) return;

    // Format relationships for D3
    const formattedRelationships = relationships.map(rel => ({
      source: parts.find(p => p.id === rel.source_id),
      target: parts.find(p => p.id === rel.target_id),
      id: rel.id,
      relationship_type: rel.relationship_type,
      description: rel.description
    })).filter(rel => rel.source && rel.target); // Ensure both source and target exist

    // Clear previous visualization
    d3.select(svgRef.current).selectAll("*").remove();

    // Setup
    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;
    const padding = 40; // Padding from edges

    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height);

    // Create a container group for all elements
    const container = svg.append("g");

    // Add zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.2, 4])
      .on("zoom", (event) => {
        container.attr("transform", event.transform);
      })
      .filter(event => {
        // Allow zoom only on wheel or dblclick events
        return event.type === 'wheel' || event.type === 'dblclick';
      });

    svg.call(zoom);

    // Create force simulation with formatted relationships
    const simulation = d3.forceSimulation(parts)
      .force("link", d3.forceLink(formattedRelationships)
        .id(d => d.id)
        .distance(150))
      .force("charge", d3.forceManyBody()
        .strength(-1000)  // Increased repulsion
        .distanceMax(width)) // Increased range
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(60))
      .force("x", d3.forceX(width / 2).strength(0.1))
      .force("y", d3.forceY(height / 2).strength(0.1));

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

    // Create node groups
    const nodeGroups = container.append("g")
      .attr("class", "nodes");

    const nodes = nodeGroups
      .selectAll("g.node")
      .data(parts)
      .enter()
      .append("g")
      .attr("class", "node")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Add circles for nodes
    const circles = nodes
      .append("circle")
      .attr("r", 20)
      .attr("fill", d => getColorForRole(d.role))
      .style("cursor", "pointer");

    // Add separate transparent circle for better click handling
    nodes.append("circle")
      .attr("r", 25)
      .attr("fill", "transparent")
      .style("cursor", "pointer")
      .on("mousedown", (event, d) => {
        console.log('Node clicked:', d.name);
        console.log('Ctrl/Cmd key pressed:', event.ctrlKey || event.metaKey);
        
        if (event.ctrlKey || event.metaKey) {
          event.preventDefault();
          event.stopPropagation();
          
          if (!relationshipStart) {
            console.log('Setting start node:', d.name);
            setRelationshipStart(d);
            
            // Highlight the selected node
            const circle = d3.select(event.target.parentNode).select("circle");
            circle
              .attr("stroke", "#000")
              .attr("stroke-width", 2)
              .attr("stroke-opacity", 1)
              .transition()
              .duration(200)
              .attr("r", 25)
              .transition()
              .duration(200)
              .attr("r", 20);
          } else if (relationshipStart.id !== d.id) {
            console.log('Setting end node:', d.name);
            setRelationshipDialog({
              open: true,
              source: relationshipStart,
              target: d,
              type: '',
              description: ''
            });
            
            // Reset all circle highlights
            circles
              .attr("stroke", null)
              .attr("stroke-width", null)
              .attr("stroke-opacity", null)
              .attr("r", 20);
            
            setRelationshipStart(null);
          }
        }
      });

    // Add labels
    nodes.append("text")
      .text(d => d.name)
      .attr("text-anchor", "middle")
      .attr("dy", 30)
      .style("font-size", "12px")
      .style("pointer-events", "none");

    // Draw relationships
    const links = container.append("g")
      .selectAll("line")
      .data(formattedRelationships)
      .enter().append("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 2)
      .attr("marker-end", "url(#arrow)")
      .style("cursor", "pointer")
      .on("click", (event, d) => {
        setRelationshipDialog({
          open: true,
          source: d.source,
          target: d.target,
          type: d.relationship_type,
          description: d.description || '',
          existing: {
            id: d.id,
            relationship_type: d.relationship_type,
            description: d.description
          }
        });
      });

    // Add relationship labels
    const linkLabels = container.append("g")
      .selectAll("text")
      .data(formattedRelationships)
      .enter().append("text")
      .attr("text-anchor", "middle")
      .attr("dy", -5)
      .text(d => d.relationship_type)
      .style("font-size", "10px")
      .style("fill", "#666")
      .style("pointer-events", "none"); // Prevent labels from interfering with clicks

    // Update positions on each tick
    simulation.on("tick", () => {
      const k = d3.zoomTransform(svg.node()).k || 1;
      
      nodes.attr("transform", d => {
        const x = Math.max(padding/k, Math.min(width - padding/k, d.x));
        const y = Math.max(padding/k, Math.min(height - padding/k, d.y));
        return `translate(${x},${y})`;
      });

      links
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      linkLabels
        .attr("x", d => (d.source.x + d.target.x) / 2)
        .attr("y", d => (d.source.y + d.target.y) / 2);
    });

    // Update drag behavior to work with zoom
    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
      simulation.alpha(0.3).restart(); // Restart simulation after drag
    }

    // Add double-click to reset zoom and center
    svg.on("dblclick.zoom", () => {
      svg.transition()
        .duration(750)
        .call(zoom.transform, d3.zoomIdentity);
      
      // Recenter nodes
      simulation.force("center", d3.forceCenter(width / 2, height / 2))
        .alpha(0.3)
        .restart();
    });

    return () => {
      simulation.stop();
    };
  }, [parts, relationships, relationshipStart]);

  const handleRelationshipSave = async () => {
    const { source, target, type, description, existing } = relationshipDialog;
    
    console.log('Saving relationship:', { source, target, type, description });  // Debug log
    
    if (!type || !source || !target) {
      console.log('Missing required fields:', { source, target, type });  // Debug log
      alert('Please select a relationship type');
      return;
    }

    try {
      if (existing) {
        console.log('Updating existing relationship:', existing);
        await onUpdateRelationship(existing.id, {
          relationship_type: type,
          description
        });
      } else {
        const relationshipData = {
          source_id: source.id,
          target_id: target.id,
          relationship_type: type,
          description
        };
        console.log('Creating new relationship:', relationshipData);  // Debug log
        await onAddRelationship(relationshipData);
      }
      
      handleDialogClose();
    } catch (error) {
      console.error('Failed to save relationship:', error);
      alert(`Failed to create relationship: ${error.message}`);
    }
  };

  const handleDialogClose = () => {
    setRelationshipDialog({
      open: false,
      source: null,
      target: null,
      type: '',
      description: ''
    });
    setRelationshipStart(null);
  };

  return (
    <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
      {relationshipStart && (
        <Alert 
          severity="info" 
          sx={{ 
            position: 'absolute', 
            top: 16, 
            left: '50%', 
            transform: 'translateX(-50%)',
            zIndex: 1 
          }}
        >
          Select another part to create a relationship from "{relationshipStart.name}"
        </Alert>
      )}

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

      <Dialog 
        open={relationshipDialog.open} 
        onClose={handleDialogClose}
      >
        <DialogTitle>
          {relationshipDialog.existing ? 'Edit Relationship' : 'Create Relationship'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            {!relationshipDialog.existing && (
              <Typography gutterBottom>
                Creating relationship from "{relationshipDialog.source?.name}" to "{relationshipDialog.target?.name}"
              </Typography>
            )}
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Relationship Type</InputLabel>
              <Select
                value={relationshipDialog.type}
                onChange={(e) => setRelationshipDialog(prev => ({
                  ...prev,
                  type: e.target.value
                }))}
                required
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
              label="Description (optional)"
              value={relationshipDialog.description}
              onChange={(e) => setRelationshipDialog(prev => ({
                ...prev,
                description: e.target.value
              }))}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button 
            onClick={handleRelationshipSave} 
            variant="contained"
            disabled={!relationshipDialog.type}
          >
            {relationshipDialog.existing ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Instructions */}
      {!relationshipStart && (
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
            • Ctrl/Cmd + Click two parts to create a relationship
            <br />
            • Click a relationship line to edit it
          </Typography>
        </Box>
      )}
    </Box>
  );
};

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

export default SystemMapVisualization; 