import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useIFS } from '../context/IFSContext';
import {
  Container,
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Avatar,
  CircularProgress,
  IconButton,
  Divider,
  Alert,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const ChatPage = () => {
  const { partId } = useParams();
  const navigate = useNavigate();
  const { system } = useIFS();
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [conversation, setConversation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);
  const part = system?.parts[partId];

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load or create a conversation on initial render
  useEffect(() => {
    if (partId) {
      fetchOrCreateConversation();
    }
  }, [partId]);

  const fetchOrCreateConversation = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      // First check if there are existing conversations
      const response = await axios.get(`${API_BASE_URL}/api/parts/${partId}/conversations`);
      
      let currentConversation;
      
      if (response.data.conversations && response.data.conversations.length > 0) {
        // Use the most recent conversation
        currentConversation = response.data.conversations[0];
      } else {
        // Create a new conversation
        const createResponse = await axios.post(
          `${API_BASE_URL}/api/parts/${partId}/conversations`,
          { title: `Conversation with ${part?.name || 'Part'}` }
        );
        currentConversation = createResponse.data.conversation;
      }
      
      setConversation(currentConversation);
      
      // Load messages for this conversation
      if (currentConversation) {
        const messagesResponse = await axios.get(
          `${API_BASE_URL}/api/conversations/${currentConversation.id}`
        );
        setMessages(messagesResponse.data.messages || []);
      }
      
    } catch (err) {
      console.error('Error fetching/creating conversation:', err);
      setError('Failed to load conversation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!message.trim() || !conversation) return;
    
    const userMessage = message.trim();
    setMessage('');
    
    // Optimistically add the user message to the UI
    const tempUserMessage = {
      id: 'temp-' + Date.now(),
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, tempUserMessage]);
    setIsLoading(true);
    
    try {
      // Send the message to the API
      const response = await axios.post(
        `${API_BASE_URL}/api/conversations/${conversation.id}/messages`,
        { content: userMessage }
      );
      
      // For debugging
      console.log('User message from server:', response.data.message);
      console.log('AI response from server:', response.data.ai_response);
      
      // Replace the temp message with the actual one and add the part's response
      setMessages(prev => {
        // Prepare the messages - ensure both user and AI messages have valid timestamps
        const userMsg = response.data.message;
        const aiMsg = response.data.ai_response;
        
        // Only process messages that exist
        const processedMessages = [];
        
        // Add user message if it exists
        if (userMsg) {
          // Ensure the user message has a timestamp
          if (!userMsg.timestamp) {
            userMsg.timestamp = new Date().toISOString();
          }
          processedMessages.push(userMsg);
        }
        
        // Add AI message if it exists
        if (aiMsg) {
          // Ensure the AI message has a timestamp
          if (!aiMsg.timestamp) {
            aiMsg.timestamp = new Date().toISOString();
          }
          processedMessages.push(aiMsg);
        }
        
        // Return the messages array without the temporary message
        return [
          ...prev.filter(m => m.id !== tempUserMessage.id),
          ...processedMessages
        ];
      });
      
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
      
      // Remove the temp message if sending failed
      setMessages(prev => prev.filter(m => m.id !== tempUserMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
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

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    
    try {
      const date = new Date(timestamp);
      // Check if the date is valid
      if (isNaN(date.getTime())) {
        return '';
      }
      
      return date.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } catch (e) {
      // If there's any error parsing the date, return an empty string
      return '';
    }
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
            Chat with {part.name}
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Paper 
          elevation={3}
          sx={{ 
            height: '60vh',
            display: 'flex',
            flexDirection: 'column',
            mb: 2,
            overflow: 'hidden'
          }}
        >
          <Box 
            sx={{ 
              p: 2, 
              flexGrow: 1,
              overflow: 'auto',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            {messages.length === 0 ? (
              <Box 
                sx={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center',
                  height: '100%',
                  color: 'text.secondary'
                }}
              >
                <Typography>
                  Start a conversation with {part.name}
                </Typography>
              </Box>
            ) : (
              messages.map((msg) => (
                <Box
                  key={msg.id}
                  sx={{
                    display: 'flex',
                    mb: 2,
                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  }}
                >
                  {msg.role !== 'user' && (
                    <Avatar 
                      sx={{ 
                        mr: 1, 
                        bgcolor: 'primary.main',
                        alignSelf: 'flex-start'
                      }}
                    >
                      {getInitials(part.name)}
                    </Avatar>
                  )}
                  <Paper
                    elevation={1}
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      backgroundColor: msg.role === 'user' ? 'primary.light' : 'background.paper',
                      color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary',
                      borderRadius: msg.role === 'user' 
                        ? '20px 20px 5px 20px' 
                        : '20px 20px 20px 5px',
                    }}
                  >
                    <Typography 
                      variant="body1"
                      sx={{ 
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word'
                      }}
                    >
                      {msg.content}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        display: 'block',
                        mt: 1,
                        textAlign: msg.role === 'user' ? 'right' : 'left',
                        color: msg.role === 'user' ? 'rgba(255,255,255,0.7)' : 'text.secondary',
                      }}
                    >
                      {formatTimestamp(msg.timestamp)}
                    </Typography>
                  </Paper>
                  {msg.role === 'user' && (
                    <Avatar 
                      sx={{ 
                        ml: 1, 
                        bgcolor: 'secondary.main',
                        alignSelf: 'flex-start'
                      }}
                    >
                      {getInitials('You')}
                    </Avatar>
                  )}
                </Box>
              ))
            )}
            {isLoading && (
              <Box 
                sx={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  p: 2 
                }}
              >
                <CircularProgress size={24} />
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Box>
          <Divider />
          <Box sx={{ p: 2, backgroundColor: 'background.paper' }}>
            <Box sx={{ display: 'flex' }}>
              <TextField
                fullWidth
                multiline
                maxRows={4}
                placeholder={`Message ${part.name}...`}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                variant="outlined"
                sx={{ mr: 1 }}
              />
              <IconButton
                color="primary"
                onClick={handleSendMessage}
                disabled={!message.trim() || isLoading}
                sx={{ alignSelf: 'flex-end', p: '10px' }}
              >
                <SendIcon />
              </IconButton>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default ChatPage; 