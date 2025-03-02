import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper, Alert } from '@mui/material';
import axios from 'axios';

// Configure API base URL - can be changed via environment variable later
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const Dashboard = () => {
  const [systemData, setSystemData] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const testConnection = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/test`);
        setConnectionStatus(response.data.message);
        setError(null);
      } catch (err) {
        setError('Failed to connect to backend server');
        console.error('Connection error:', err);
      }
    };

    const fetchSystem = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/system`);
        setSystemData(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch system data');
        console.error('Error fetching system data:', err);
      }
    };

    testConnection();
    fetchSystem();
  }, []);

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          IFS System Dashboard
        </Typography>

        {/* Connection Status */}
        {connectionStatus && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {connectionStatus}
          </Alert>
        )}
        
        {/* Error Message */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6">System Overview</Typography>
              <Typography>
                Total Parts: {systemData ? Object.keys(systemData.parts).length : 0}
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6">Recent Activity</Typography>
              {/* Add recent activity content here */}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Dashboard; 