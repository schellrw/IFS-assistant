import React, { useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useIFS } from '../context/IFSContext';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import { InputField, TextArea, RoleSelector, FeelingsInput, ListInput } from '../components';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { ROLE_OPTIONS } from '../constants';

// const ROLE_OPTIONS = [
//   { value: 'protector', label: 'Protector' },
//   { value: 'exile', label: 'Exile' },
//   { value: 'manager', label: 'Manager' },
//   { value: 'firefighter', label: 'Firefighter' },
//   { value: 'self', label: 'Self' },
// ];

const PartDetailsPage = () => {
  const { partId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { system, updatePart, deletePart } = useIFS();
  const [isEditing, setIsEditing] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [error, setError] = useState('');

  const part = system?.parts[partId];
  const [formData, setFormData] = useState(part || {});

  // Get the backLink from URL params
  const backLink = searchParams.get('backLink');

  // Update the back button
  const handleBack = () => {
    if (backLink === 'system-map') {
      navigate('/system-map');
    } else {
      navigate('/parts');
    }
  };

  if (!part) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">Part not found</Alert>
      </Container>
    );
  }

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    try {
      await updatePart(partId, formData);
      setIsEditing(false);
      setError('');
    } catch (err) {
      setError('Failed to update part');
      console.error('Error updating part:', err);
    }
  };

  const handleDelete = async () => {
    try {
      await deletePart(partId);
      navigate('/parts');
    } catch (err) {
      setError('Failed to delete part');
      console.error('Error deleting part:', err);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBack}
          sx={{ mb: 2 }}
        >
          {backLink === 'system-map' ? 'Back to System Map' : 'Back to Parts'}
        </Button>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4" component="h1">
            {isEditing ? 'Edit Part' : part.name}
          </Typography>
          <Stack direction="row" spacing={2}>
            {!isEditing && (
              <>
                <Button
                  variant="outlined"
                  startIcon={<EditIcon />}
                  onClick={() => setIsEditing(true)}
                >
                  Edit
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={() => setDeleteDialog(true)}
                >
                  Delete
                </Button>
              </>
            )}
          </Stack>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Paper sx={{ p: 3 }}>
          {isEditing ? (
            <Stack spacing={2}>
              <InputField
                label="Part Name"
                value={formData.name}
                onChange={(value) => handleChange('name', value)}
                required
              />

              <RoleSelector
                label="Role"
                options={ROLE_OPTIONS}
                value={formData.role}
                onChange={(value) => handleChange('role', value)}
              />

              <TextArea
                label="Description"
                value={formData.description}
                onChange={(value) => handleChange('description', value)}
              />

              <FeelingsInput
                label="Associated Feelings"
                value={formData.feelings}
                onChange={(value) => handleChange('feelings', value)}
              />

              <ListInput
                label="Core Beliefs"
                value={formData.beliefs || []}
                onChange={(value) => handleChange('beliefs', value)}
                placeholder="Enter a core belief..."
              />

              <ListInput
                label="Triggers"
                value={formData.triggers || []}
                onChange={(value) => handleChange('triggers', value)}
                placeholder="Enter a trigger..."
              />

              <ListInput
                label="Needs"
                value={formData.needs || []}
                onChange={(value) => handleChange('needs', value)}
                placeholder="Enter a need..."
              />

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button onClick={() => setIsEditing(false)}>Cancel</Button>
                <Button variant="contained" onClick={handleSave}>
                  Save Changes
                </Button>
              </Box>
            </Stack>
          ) : (
            <Stack spacing={2}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Role</Typography>
                <Typography>{part.role || 'No role specified'}</Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary">Description</Typography>
                <Typography>{part.description || 'No description'}</Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary">Feelings</Typography>
                <Typography>{part.feelings?.join(', ') || 'No feelings specified'}</Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary">Core Beliefs</Typography>
                <ul>
                  {part.beliefs?.map((belief, index) => (
                    <li key={index}>{belief}</li>
                  )) || <Typography>No beliefs specified</Typography>}
                </ul>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary">Triggers</Typography>
                <ul>
                  {part.triggers?.map((trigger, index) => (
                    <li key={index}>{trigger}</li>
                  )) || <Typography>No triggers specified</Typography>}
                </ul>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary">Needs</Typography>
                <ul>
                  {part.needs?.map((need, index) => (
                    <li key={index}>{need}</li>
                  )) || <Typography>No needs specified</Typography>}
                </ul>
              </Box>
            </Stack>
          )}
        </Paper>

        <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
          <DialogTitle>Delete Part</DialogTitle>
          <DialogContent>
            Are you sure you want to delete {part.name}? This action cannot be undone.
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteDialog(false)}>Cancel</Button>
            <Button onClick={handleDelete} color="error" variant="contained">
              Delete
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default PartDetailsPage; 