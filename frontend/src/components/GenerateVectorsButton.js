import React, { useState } from 'react';
import {
  Button,
  CircularProgress,
  Snackbar,
  Alert
} from '@mui/material';
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

/**
 * Button component for generating personality vectors for a part.
 * This component sends a request to generate vector embeddings for the part,
 * which enables semantic search functionality.
 */
const GenerateVectorsButton = ({ partId, variant = 'outlined', size = 'medium' }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });

  const handleGenerateVectors = async () => {
    if (!partId) return;
    
    setIsLoading(true);
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/parts/${partId}/personality-vectors`
      );
      
      setSnackbar({
        open: true,
        message: 'Personality vectors generated successfully!',
        severity: 'success'
      });
      
    } catch (err) {
      console.error('Error generating vectors:', err);
      
      setSnackbar({
        open: true,
        message: 'Failed to generate vectors. Please try again.',
        severity: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <>
      <Button
        variant={variant}
        size={size}
        color="primary"
        onClick={handleGenerateVectors}
        disabled={isLoading}
        startIcon={isLoading ? <CircularProgress size={20} /> : <SettingsSuggestIcon />}
      >
        {isLoading ? 'Generating...' : 'Generate Vectors'}
      </Button>
      
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default GenerateVectorsButton; 