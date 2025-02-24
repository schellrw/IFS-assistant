import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
import { InputField, TextArea, RoleSelector, FeelingsInput } from '../components';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

const ROLE_OPTIONS = [
  { value: 'protector', label: 'Protector' },
  { value: 'exile', label: 'Exile' },
  { value: 'manager', label: 'Manager' },
  { value: 'firefighter', label: 'Firefighter' },
  { value: 'self', label: 'Self' },
];

const PartDetailsPage = () => {
  const { partId } = useParams();
  const navigate = useNavigate();
  const { system, updatePart, deletePart } = useIFS();
  const [isEditing, setIsEditing] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [error, setError] = useState('');

  const part = system?.parts[partId];
  const [formData, setFormData] = useState(part || {});

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
          onClick={() => navigate('/parts')}
          sx={{ mb: 2 }}
        >
          Back to Parts
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

              <TextArea
                label="Core Beliefs"
                value={formData.beliefs?.join('\n')}
                onChange={(value) => handleChange('beliefs', value.split('\n').filter(b => b.trim()))}
                placeholder="Enter one belief per line"
              />

              <TextArea
                label="Triggers"
                value={formData.triggers?.join('\n')}
                onChange={(value) => handleChange('triggers', value.split('\n').filter(t => t.trim()))}
                placeholder="Enter one trigger per line"
              />

              <TextArea
                label="Needs"
                value={formData.needs?.join('\n')}
                onChange={(value) => handleChange('needs', value.split('\n').filter(n => n.trim()))}
                placeholder="Enter one need per line"
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