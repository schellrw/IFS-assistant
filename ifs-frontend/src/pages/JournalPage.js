import React, { useState } from 'react';
import { useIFS } from '../context/IFSContext';
import { Container, Typography, Box } from '@mui/material';
import { EmotionPicker, PartSelector, ReflectivePrompt } from '../components';

const JournalPage = () => {
  // Basic implementation for now
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Journal
        </Typography>
        {/* We'll implement the full journal functionality later */}
      </Box>
    </Container>
  );
};

export default JournalPage; 