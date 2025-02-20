import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Navigation = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          IFS Explorer
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button color="inherit" component={RouterLink} to="/">
            Dashboard
          </Button>
          <Button color="inherit" component={RouterLink} to="/parts">
            Parts
          </Button>
          <Button color="inherit" component={RouterLink} to="/journal">
            Journal
          </Button>
          <Button color="inherit" component={RouterLink} to="/system-map">
            System Map
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navigation; 