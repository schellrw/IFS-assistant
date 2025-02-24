import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useIFS } from '../context/IFSContext';
import {
  Container,
  Typography,
  Button,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
} from '@mui/material';
import { NewPartForm } from '../components';
import AddIcon from '@mui/icons-material/Add';

const PartsPage = () => {
  const [newPartDialog, setNewPartDialog] = useState(false);
  const { addPart } = useIFS();
  const navigate = useNavigate();

  const handleCreatePart = async (formData) => {
    try {
      // Make sure arrays are properly initialized
      const newPart = {
        ...formData,
        feelings: formData.feelings || [],
        beliefs: formData.beliefs || [],
        triggers: formData.triggers || [],
        needs: formData.needs || []
      };
      
      const response = await addPart(newPart);
      setNewPartDialog(false);
      navigate(`/parts/${response.id}`);
    } catch (error) {
      console.error('Error creating part:', error);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4 }}>
          <Typography variant="h4" component="h1">
            Parts
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setNewPartDialog(true)}
          >
            New Part
          </Button>
        </Box>

        {/* Parts list rendering... */}

        <Dialog 
          open={newPartDialog} 
          onClose={() => setNewPartDialog(false)}
          maxWidth="md"
          fullWidth
          PaperProps={{
            sx: {
              minHeight: '80vh',
              maxHeight: '90vh'
            }
          }}
        >
          <DialogTitle>Create New Part</DialogTitle>
          <DialogContent sx={{ 
            pb: 3,
            pt: 2,
            px: 3,
            '& .MuiDialogContent-root': {
              padding: 0
            }
          }}>
            <NewPartForm
              onSubmit={handleCreatePart}
              onCancel={() => setNewPartDialog(false)}
            />
          </DialogContent>
        </Dialog>
      </Box>
    </Container>
  );
};

export default PartsPage; 