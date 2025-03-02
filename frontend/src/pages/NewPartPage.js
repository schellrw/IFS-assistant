import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useIFS } from '../context/IFSContext';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Stack,
  Alert,
} from '@mui/material';
import { InputField, TextArea, RoleSelector, FeelingsInput, ListInput } from '../components';
import { ROLE_OPTIONS } from '../constants';

// const ROLE_OPTIONS = [
//   { value: 'protector', label: 'Protector' },
//   { value: 'exile', label: 'Exile' },
//   { value: 'manager', label: 'Manager' },
//   { value: 'firefighter', label: 'Firefighter' },
//   { value: 'self', label: 'Self' },
// ];

const NewPartPage = () => {
  const navigate = useNavigate();
  const { addPart } = useIFS();
  const [formData, setFormData] = useState({
    name: '',
    role: '',
    description: '',
    feelings: [],
    beliefs: [],
    triggers: [],
    needs: [],
  });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const handleChange = (field, value) => {
    console.log(`NewPartPage - Updating ${field}:`, value);
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('NewPartPage - Submitting form data:', formData);
    if (!formData.name.trim()) {
      setError('Part name is required');
      return;
    }

    try {
      setSaving(true);
      await addPart(formData);
      navigate('/parts');
    } catch (err) {
      setError('Failed to create part. Please try again.');
      console.error('Error creating part:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Add New Part
        </Typography>

        <form onSubmit={handleSubmit}>
          <Stack spacing={3}>
            {error && (
              <Alert severity="error" onClose={() => setError('')}>
                {error}
              </Alert>
            )}

            <Paper sx={{ p: 3 }}>
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
              </Stack>
            </Paper>

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                variant="outlined"
                onClick={() => navigate('/parts')}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Create Part'}
              </Button>
            </Box>
          </Stack>
        </form>
      </Box>
    </Container>
  );
};

export default NewPartPage; 