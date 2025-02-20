import React from 'react';
import { Container, Typography, Box, Paper, Alert } from '@mui/material';
import { useIFS } from '../context/IFSContext';
import { SystemMapVisualization } from '../components';

const SystemMapPage = () => {
  const { system, loading, error } = useIFS();

  if (loading) {
    return (
      <Container sx={{ mt: 4, textAlign: 'center' }}>
        <Typography>Loading system map...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          System Map
        </Typography>
        <Paper sx={{ p: 2, height: '70vh' }}>
          <SystemMapVisualization 
            parts={Object.values(system?.parts || {})}
            relationships={Object.values(system?.relationships || {})}
          />
        </Paper>
      </Box>
    </Container>
  );
};

export default SystemMapPage; 