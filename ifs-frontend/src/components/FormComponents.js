import React from 'react';
import { TextField, MenuItem, Chip, Box } from '@mui/material';

export const InputField = ({ label, value, onChange, required = false }) => (
  <TextField
    fullWidth
    label={label}
    value={value}
    onChange={(e) => onChange(e.target.value)}
    required={required}
    margin="normal"
  />
);

export const TextArea = ({ label, value, onChange, rows = 4 }) => (
  <TextField
    fullWidth
    multiline
    rows={rows}
    label={label}
    value={value}
    onChange={(e) => onChange(e.target.value)}
    margin="normal"
  />
);

export const RoleSelector = ({ label, options, value, onChange }) => (
  <TextField
    select
    fullWidth
    label={label}
    value={value}
    onChange={(e) => onChange(e.target.value)}
    margin="normal"
  >
    {options.map((option) => (
      <MenuItem key={option.value} value={option.value}>
        {option.label}
      </MenuItem>
    ))}
  </TextField>
);

export const FeelingsInput = ({ label, value, onChange }) => {
  const [inputValue, setInputValue] = React.useState('');

  const handleAdd = (feeling) => {
    if (feeling && !value.includes(feeling)) {
      onChange([...value, feeling]);
    }
    setInputValue('');
  };

  const handleDelete = (feelingToDelete) => {
    onChange(value.filter((feeling) => feeling !== feelingToDelete));
  };

  return (
    <Box sx={{ mt: 2 }}>
      <TextField
        fullWidth
        label={label}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
            handleAdd(inputValue);
          }
        }}
        margin="normal"
      />
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
        {value.map((feeling) => (
          <Chip
            key={feeling}
            label={feeling}
            onDelete={() => handleDelete(feeling)}
          />
        ))}
      </Box>
    </Box>
  );
}; 