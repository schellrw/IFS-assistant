import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useIFS } from '../context/IFSContext';
import {
  Container,
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  ListItemAvatar,
  Avatar,
  Button,
  TextField,
  InputAdornment,
  IconButton,
  Alert,
  CircularProgress,
  Divider,
  Chip,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SearchIcon from '@mui/icons-material/Search';
import ChatIcon from '@mui/icons-material/Chat';
import AddIcon from '@mui/icons-material/Add';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const ConversationsPage = () => {
  const { partId } = useParams();
  const navigate = useNavigate();
  const { system } = useIFS();
  const [conversations, setConversations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchMode, setSearchMode] = useState('text'); // 'text' or 'semantic'
  
  const part = system?.parts[partId];

  useEffect(() => {
    if (partId) {
      fetchConversations();
    }
  }, [partId]);

  const fetchConversations = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/parts/${partId}/conversations`);
      setConversations(response.data.conversations || []);
    } catch (err) {
      console.error('Error fetching conversations:', err);
      setError('Failed to load conversations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const createNewConversation = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/parts/${partId}/conversations`,
        { title: `New Conversation with ${part?.name || 'Part'}` }
      );
      
      // Navigate to the new conversation
      navigate(`/chat/${partId}?conversation=${response.data.conversation.id}`);
      
    } catch (err) {
      console.error('Error creating conversation:', err);
      setError('Failed to create a new conversation. Please try again.');
      setIsLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchConversations();
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/conversations/search?query=${encodeURIComponent(searchQuery)}&part_id=${partId}&search_type=${searchMode}`
      );
      
      setConversations(response.data.conversations || []);
      
    } catch (err) {
      console.error('Error searching conversations:', err);
      setError('Search failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getInitials = (name) => {
    return name
      ? name
          .split(' ')
          .map(part => part[0])
          .join('')
          .toUpperCase()
      : '?';
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    
    // If today, just show time
    const today = new Date();
    if (date.toDateString() === today.toDateString()) {
      return `Today, ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    }
    
    // If this year, show month and day
    if (date.getFullYear() === today.getFullYear()) {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
    
    // Otherwise show full date
    return date.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' });
  };

  if (!part) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">Part not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(`/parts/${partId}`)}
          sx={{ mb: 2 }}
        >
          Back to Part Details
        </Button>

        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Avatar 
            sx={{ 
              bgcolor: 'primary.main',
              mr: 2,
              width: 56,
              height: 56
            }}
          >
            {getInitials(part.name)}
          </Avatar>
          <Typography variant="h4" component="h1">
            Conversations with {part.name}
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Paper sx={{ p: 2, mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <TextField
              fullWidth
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleSearch}>
                      <SearchIcon />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ mr: 2 }}
            />
            <Box>
              <Chip
                label="Text"
                color={searchMode === 'text' ? 'primary' : 'default'}
                onClick={() => setSearchMode('text')}
                sx={{ mr: 1 }}
              />
              <Chip
                label="Semantic"
                color={searchMode === 'semantic' ? 'primary' : 'default'}
                onClick={() => setSearchMode('semantic')}
              />
            </Box>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={createNewConversation}
            fullWidth
          >
            Start New Conversation
          </Button>
        </Paper>

        <Paper elevation={1}>
          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : conversations.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                No conversations found.
              </Typography>
              <Button
                variant="outlined"
                startIcon={<ChatIcon />}
                onClick={createNewConversation}
                sx={{ mt: 2 }}
              >
                Start your first conversation
              </Button>
            </Box>
          ) : (
            <List>
              {conversations.map((conversation, index) => (
                <React.Fragment key={conversation.id}>
                  {index > 0 && <Divider component="li" />}
                  <ListItem disablePadding>
                    <ListItemButton
                      onClick={() => navigate(`/chat/${partId}?conversation=${conversation.id}`)}
                    >
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          <ChatIcon />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={conversation.title || `Conversation with ${part.name}`}
                        secondary={formatDate(conversation.created_at)}
                        primaryTypographyProps={{
                          fontWeight: 'medium',
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default ConversationsPage; 