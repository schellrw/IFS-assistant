import React from 'react';
import { Paper, Typography, Box } from '@mui/material';

export const ReflectivePrompt = ({ text }) => {
  return (
    <Paper sx={{ p: 2, mb: 2, bgcolor: 'primary.light' }}>
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <Typography 
          variant="body1" 
          color="primary.contrastText"
          sx={{ fontStyle: 'italic' }}
        >
          {text}
        </Typography>
      </Box>
    </Paper>
  );
}; 