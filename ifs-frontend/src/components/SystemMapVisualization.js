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
      .attr("fill", d => getColorForRole(d.role))
      .style("cursor", "pointer")
      .on("click", (event, d) => {
        if (event.ctrlKey || event.metaKey) {
          event.preventDefault();
          if (!relationshipStart) {
            setRelationshipStart(d);
            // Highlight the selected node
            d3.select(event.target).attr("stroke", "#000").attr("stroke-width", 2);
          } else if (relationshipStart.id !== d.id) {
            // Open dialog for creating relationship
            setRelationshipDialog({
              open: true,
              source: relationshipStart,
              target: d,
              type: '',
              description: ''
            });
            // Reset highlight
            nodes.selectAll("circle").attr("stroke", null);
            setRelationshipStart(null);
          }
        }
      });

    // Add labels
    nodes.append("text")
      .text(d => d.name)
      .attr("text-anchor", "middle")
      .attr("dy", 30)
      .style("font-size", "12px");

    // Draw relationships
    const links = svg.append("g")
      .selectAll("line")
      .data(relationships)
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
          existing: d
        });
      });

    // Update positions on each tick
    simulation.on("tick", () => {
      links
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      nodes.attr("transform", d => `translate(${d.x},${d.y})`);
    });

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

    return () => {
      simulation.stop();
    };
  }, [parts, relationships, relationshipStart]);

  const handleRelationshipSave = () => {
    const { source, target, type, description, existing } = relationshipDialog;
    
    if (!type) {
      return; // Don't save without a type
    }

    if (existing) {
      onUpdateRelationship(existing.id, {
        relationship_type: type,
        description
      });
    } else {
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