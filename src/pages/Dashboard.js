import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Grid, Paper } from '@mui/material';
import axios from 'axios';

const Dashboard = () => {
  const [systemData, setSystemData] = useState(null);

  useEffect(() => {
    const fetchSystem = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/system');
        setSystemData(response.data);
      } catch (error) {
        console.error('Error fetching system data:', error);
      }
    };

    fetchSystem();
  }, []);

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          IFS System Dashboard
        </Typography>
        
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