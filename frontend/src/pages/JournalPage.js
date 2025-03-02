import React, { useState, useEffect } from 'react';
import { useIFS } from '../context/IFSContext';
import { 
  Container, Typography, Box, Paper, TextField, Button,
  Stack, Alert
} from '@mui/material';
import { EmotionPicker, PartSelector, ReflectivePrompt } from '../components';

const REFLECTIVE_PROMPTS = [
  "What am I feeling in my body right now?",
  "Which parts of me are present in this moment?",
  "What does this part want me to know?",
  "How does Self feel toward this part?",
  "What does this part need?"
];

const COMMON_EMOTIONS = [
  { id: 'anger', label: 'Anger', color: '#ff4d4d' },
  { id: 'fear', label: 'Fear', color: '#9370db' },
  { id: 'sadness', label: 'Sadness', color: '#4169e1' },
  { id: 'shame', label: 'Shame', color: '#8b4513' },
  { id: 'joy', label: 'Joy', color: '#ffd700' },
  { id: 'peace', label: 'Peace', color: '#98fb98' },
  { id: 'curiosity', label: 'Curiosity', color: '#ff69b4' },
  { id: 'compassion', label: 'Compassion', color: '#dda0dd' }
];

const JournalPage = () => {
  const { system, loading, error, addJournal } = useIFS();
  const [content, setContent] = useState('');
  const [selectedEmotions, setSelectedEmotions] = useState([]);
  const [selectedParts, setSelectedParts] = useState([]);
  const [currentPrompt, setCurrentPrompt] = useState(REFLECTIVE_PROMPTS[0]);
  const [saveStatus, setSaveStatus] = useState({ type: '', message: '' });

  useEffect(() => {
    // Rotate prompts every 30 seconds
    const interval = setInterval(() => {
      setCurrentPrompt(prev => {
        const currentIndex = REFLECTIVE_PROMPTS.indexOf(prev);
        const nextIndex = (currentIndex + 1) % REFLECTIVE_PROMPTS.length;
        return REFLECTIVE_PROMPTS[nextIndex];
      });
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleSave = async () => {
    try {
      setSaveStatus({ type: 'info', message: 'Saving...' });
      
      const journalEntry = {
        content,
        emotions: selectedEmotions,
        parts_present: selectedParts
      };

      await addJournal(journalEntry);
      
      setSaveStatus({ type: 'success', message: 'Journal entry saved successfully!' });
      
      // Clear form after successful save
      setContent('');
      setSelectedEmotions([]);
      setSelectedParts([]);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSaveStatus({ type: '', message: '' });
      }, 3000);
    } catch (err) {
      setSaveStatus({ 
        type: 'error', 
        message: 'Failed to save journal entry. Please try again.' 
      });
    }
  };

  if (loading) {
    return (
      <Container sx={{ mt: 4, textAlign: 'center' }}>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  const parts = system ? Object.values(system.parts) : [];

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Journal
        </Typography>

        <Stack spacing={3}>
          {/* Reflective Prompt */}
          <ReflectivePrompt text={currentPrompt} />

          {/* Emotion Picker */}
          <Paper sx={{ p: 2 }}>
            <EmotionPicker
              emotions={COMMON_EMOTIONS}
              selectedEmotions={selectedEmotions}
              onChange={setSelectedEmotions}
            />
          </Paper>

          {/* Part Selector */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Parts Present:
            </Typography>
            <PartSelector
              parts={parts}
              selectedParts={selectedParts}
              onChange={setSelectedParts}
            />
          </Paper>

          {/* Journal Content */}
          <Paper sx={{ p: 2 }}>
            <TextField
              fullWidth
              multiline
              rows={6}
              label="What's coming up for you?"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              variant="outlined"
            />
          </Paper>

          {/* Save Button and Status */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSave}
              disabled={!content.trim()}
            >
              Save Entry
            </Button>
            {saveStatus.message && (
              <Alert severity={saveStatus.type} sx={{ flexGrow: 1, ml: 2 }}>
                {saveStatus.message}
              </Alert>
            )}
          </Box>
        </Stack>
      </Box>
    </Container>
  );
};

export default JournalPage; 