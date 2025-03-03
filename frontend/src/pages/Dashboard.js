import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, Box, Grid, Paper, Alert, List, ListItem,
  ListItemText, ListItemIcon, Divider, Button, Chip, CircularProgress,
  Card, CardContent, CardActions, IconButton, Tooltip
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import EditNoteIcon from '@mui/icons-material/EditNote';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import UpdateIcon from '@mui/icons-material/Update';
import EmojiPeopleIcon from '@mui/icons-material/EmojiPeople';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import RefreshIcon from '@mui/icons-material/Refresh';
import { format, formatDistanceToNow, differenceInDays } from 'date-fns';
import { useIFS } from '../context/IFSContext';
import { REFLECTIVE_PROMPTS } from '../constants';
import axios from 'axios';

// Configure API base URL - can be changed via environment variable later
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const Dashboard = () => {
  const { system, loading: ifsLoading, error: ifsError, journals, getJournals } = useIFS();
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [error, setError] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loadingActivity, setLoadingActivity] = useState(true);
  const [currentPrompt, setCurrentPrompt] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  // Get a random reflective prompt
  const getRandomPrompt = () => {
    const randomIndex = Math.floor(Math.random() * REFLECTIVE_PROMPTS.length);
    return REFLECTIVE_PROMPTS[randomIndex];
  };

  // Refresh the reflective prompt
  const refreshPrompt = () => {
    const newPrompt = getRandomPrompt();
    setCurrentPrompt(newPrompt);
    localStorage.setItem('currentJournalPrompt', newPrompt);
  };

  // Initialize prompt on component mount - either from localStorage or a new random one
  useEffect(() => {
    const savedPrompt = localStorage.getItem('currentJournalPrompt');
    if (savedPrompt && REFLECTIVE_PROMPTS.includes(savedPrompt)) {
      setCurrentPrompt(savedPrompt);
    } else {
      const newPrompt = getRandomPrompt();
      setCurrentPrompt(newPrompt);
      localStorage.setItem('currentJournalPrompt', newPrompt);
    }
  }, []);

  useEffect(() => {
    const testConnection = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/test`);
        setConnectionStatus(response.data.message);
        setError(null);
      } catch (err) {
        setError('Failed to connect to backend server');
        console.error('Connection error:', err);
      }
    };

    testConnection();
  }, []);

  useEffect(() => {
    const fetchRecentActivity = async () => {
      setLoadingActivity(true);
      try {
        // Fetch journals if they aren't already loaded
        const journalData = journals.length > 0 ? journals : await getJournals();
        
        // Create combined activity list
        const allActivity = [];
        
        // Add journal entries to activity
        if (journalData && journalData.length > 0) {
          journalData.slice(0, 5).forEach(journal => {
            allActivity.push({
              type: 'journal',
              id: journal.id,
              title: journal.title,
              timestamp: new Date(journal.date),
              associatedId: journal.part_id
            });
          });
        }
        
        // Add part creation/updates to activity
        if (system && system.parts) {
          Object.values(system.parts).forEach(part => {
            // Skip the default "Self" part for activity tracking
            if (part.name !== 'Self') {
              if (part.created_at) {
                allActivity.push({
                  type: 'part_created',
                  id: part.id,
                  title: `Part "${part.name}" created`,
                  timestamp: new Date(part.created_at),
                  associatedId: part.id
                });
              }
              
              if (part.updated_at && part.updated_at !== part.created_at) {
                allActivity.push({
                  type: 'part_updated',
                  id: part.id + '_update',
                  title: `Part "${part.name}" updated`,
                  timestamp: new Date(part.updated_at),
                  associatedId: part.id
                });
              }
            }
          });
        }
        
        // Add relationships to activity
        if (system && system.relationships) {
          Object.values(system.relationships).forEach(rel => {
            const sourcePart = system.parts[rel.source_id]?.name || 'Unknown';
            const targetPart = system.parts[rel.target_id]?.name || 'Unknown';
            
            allActivity.push({
              type: 'relationship',
              id: rel.id,
              title: `Relationship created: "${sourcePart}" → "${targetPart}"`,
              timestamp: new Date(rel.created_at),
              associatedId: rel.id
            });
          });
        }
        
        // Sort by timestamp (newest first) and take top 10
        const sortedActivity = allActivity
          .sort((a, b) => b.timestamp - a.timestamp)
          .slice(0, 10);
          
        setRecentActivity(sortedActivity);
      } catch (err) {
        console.error('Error fetching activity data:', err);
      } finally {
        setLoadingActivity(false);
      }
    };
    
    if (system || journals.length > 0) {
      fetchRecentActivity();
    }
  }, [system, journals, getJournals]);

  // Generate personalized recommendations based on system data
  useEffect(() => {
    if (!system || ifsLoading) return;
    
    const generateRecommendations = () => {
      const newRecommendations = [];
      
      // Check if user has any journal entries
      const hasJournals = journals && journals.length > 0;
      
      // Check when was the last journal entry
      const lastJournalDate = hasJournals 
        ? new Date(journals[0].date) 
        : null;
        
      const daysSinceLastJournal = lastJournalDate 
        ? differenceInDays(new Date(), lastJournalDate) 
        : null;
      
      // Check if the user has created any parts (besides Self)
      const userParts = system.parts ? Object.values(system.parts).filter(part => part.name !== 'Self') : [];
      const hasCustomParts = userParts.length > 0;
      
      // Check if there are any relationships between parts
      const hasRelationships = system.relationships && system.relationships.length > 0;
      
      // Recommendation 1: Journaling recommendation
      if (!hasJournals) {
        newRecommendations.push({
          id: 'journal_first',
          type: 'journal',
          title: 'Start Your Journal',
          description: 'Journaling helps track your progress and insights. Try writing your first entry.',
          action: () => navigate('/journal', { 
            state: { selectedPrompt: currentPrompt } 
          })
        });
      } else if (daysSinceLastJournal > 3) {
        newRecommendations.push({
          id: 'journal_reminder',
          type: 'journal',
          title: 'Time for a Journal Check-in',
          description: `It's been ${daysSinceLastJournal} days since your last journal entry. Consider checking in with how you're feeling today.`,
          action: () => navigate('/journal', { 
            state: { selectedPrompt: currentPrompt } 
          })
        });
      }
      
      // Recommendation 2: Parts creation
      if (!hasCustomParts) {
        newRecommendations.push({
          id: 'create_first_part',
          type: 'part',
          title: 'Identify Your First Part',
          description: 'Start by identifying one part of your internal system. What part of you do you notice most often?',
          action: () => navigate('/parts/new')
        });
      } else if (userParts.length < 3) {
        newRecommendations.push({
          id: 'create_more_parts',
          type: 'part',
          title: 'Discover More Parts',
          description: 'Most people have many different parts. Try identifying more parts that you notice in your daily life.',
          action: () => navigate('/parts/new')
        });
      }
      
      // Recommendation 3: Relationships between parts
      if (hasCustomParts && !hasRelationships && userParts.length > 1) {
        newRecommendations.push({
          id: 'create_relationships',
          type: 'relationship',
          title: 'Connect Your Parts',
          description: 'Explore how your parts might relate to each other by creating relationships in your system map.',
          action: () => navigate('/system-map')
        });
      }
      
      // Recommendation 4: Check in with a specific part
      if (hasCustomParts && userParts.length > 0) {
        // Find a part that hasn't been updated recently or pick a random one
        let partToCheckIn = userParts[0];
        
        // If we have multiple parts, try to find one that hasn't been updated recently
        if (userParts.length > 1) {
          const partsWithDates = userParts
            .filter(part => part.updated_at)
            .sort((a, b) => new Date(a.updated_at) - new Date(b.updated_at));
            
          if (partsWithDates.length > 0) {
            partToCheckIn = partsWithDates[0];
          }
        }
        
        newRecommendations.push({
          id: `checkin_${partToCheckIn.id}`,
          type: 'part_checkin',
          title: `Check in with "${partToCheckIn.name}"`,
          description: `It might be a good time to check in with your "${partToCheckIn.name}" part and see how it's doing.`,
          action: () => navigate(`/parts/${partToCheckIn.id}`)
        });
      }
      
      // Shuffle and limit recommendations to 3
      const shuffled = newRecommendations.sort(() => 0.5 - Math.random());
      setRecommendations(shuffled.slice(0, 3));
    };
    
    generateRecommendations();
  }, [system, journals, ifsLoading, navigate]);

  const handleActivityClick = (type, id) => {
    if (type === 'journal') {
      navigate('/journal', { 
        state: { 
          highlightId: id,
          selectedPrompt: currentPrompt 
        } 
      });
    } else if (type === 'part_created' || type === 'part_updated') {
      navigate(`/parts/${id}`);
    } else if (type === 'relationship') {
      navigate('/system-map');
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'journal':
        return <EditNoteIcon color="primary" />;
      case 'part_created':
        return <PersonAddIcon color="secondary" />;
      case 'part_updated':
        return <UpdateIcon color="secondary" />;
      case 'relationship':
        return <CompareArrowsIcon color="info" />;
      default:
        return <EditNoteIcon />;
    }
  };

  const getRecommendationIcon = (type) => {
    switch (type) {
      case 'journal':
        return <EditNoteIcon color="primary" />;
      case 'part':
        return <PersonAddIcon color="secondary" />;
      case 'relationship':
        return <CompareArrowsIcon color="info" />;
      case 'part_checkin':
        return <EmojiPeopleIcon color="secondary" />;
      default:
        return <LightbulbIcon color="primary" />;
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          IFS System Dashboard
        </Typography>

        {/* Connection Status */}
        {connectionStatus && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {connectionStatus}
          </Alert>
        )}
        
        {/* Error Message */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {ifsError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {ifsError}
          </Alert>
        )}
        
        <Grid container spacing={3}>
          {/* System Overview */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, height: '100%' }}>
              <Typography variant="h6" gutterBottom>System Overview</Typography>
              
              {ifsLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : (
                <>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 2 }}>
                    <Typography>
                      Total Parts: {system ? Object.keys(system.parts).length : 0}
                    </Typography>
                    <Typography>
                      Relationships: {system?.relationships ? Object.keys(system.relationships).length : 0}
                    </Typography>
                    <Typography>
                      Journal Entries: {journals?.length || 0}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1, mt: 3, flexWrap: 'wrap' }}>
                    <Button 
                      variant="contained" 
                      size="small" 
                      onClick={() => navigate('/parts/new')}
                    >
                      Add New Part
                    </Button>
                    <Button 
                      variant="outlined" 
                      size="small" 
                      onClick={() => navigate('/journal', { 
                        state: { selectedPrompt: currentPrompt } 
                      })}
                    >
                      Write Journal Entry
                    </Button>
                    <Button 
                      variant="outlined" 
                      size="small" 
                      onClick={() => navigate('/system-map')}
                    >
                      Explore System Map
                    </Button>
                  </Box>
                </>
              )}
            </Paper>
          </Grid>
          
          {/* Recent Activity */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, height: '100%' }}>
              <Typography variant="h6" gutterBottom>Recent Activity</Typography>
              
              {loadingActivity || ifsLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : recentActivity.length > 0 ? (
                <List dense sx={{ maxHeight: '400px', overflow: 'auto' }}>
                  {recentActivity.map((activity, index) => (
                    <React.Fragment key={activity.id}>
                      {index > 0 && <Divider variant="inset" component="li" />}
                      <ListItem 
                        button 
                        onClick={() => handleActivityClick(activity.type, activity.associatedId)}
                        alignItems="flex-start"
                      >
                        <ListItemIcon>
                          {getActivityIcon(activity.type)}
                        </ListItemIcon>
                        <ListItemText
                          primary={activity.title}
                          secondary={
                            <>
                              <Typography
                                sx={{ display: 'block' }}
                                component="span"
                                variant="body2"
                                color="text.primary"
                              >
                                {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
                              </Typography>
                              <Typography
                                component="span"
                                variant="caption"
                                color="text.secondary"
                              >
                                {format(activity.timestamp, 'PPP p')}
                              </Typography>
                            </>
                          }
                        />
                      </ListItem>
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Box sx={{ p: 2, textAlign: 'center' }}>
                  <Typography color="text.secondary">
                    No recent activity found. Start by adding parts or writing journal entries.
                  </Typography>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    sx={{ mt: 2 }}
                    onClick={() => navigate('/parts/new')}
                  >
                    Add Your First Part
                  </Button>
                </Box>
              )}
            </Paper>
          </Grid>
          
          {/* Recommendations */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Recommended Next Steps
            </Typography>
            <Grid container spacing={2}>
              {ifsLoading ? (
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                    <CircularProgress size={24} />
                  </Box>
                </Grid>
              ) : recommendations.length > 0 ? (
                recommendations.map(rec => (
                  <Grid item xs={12} md={4} key={rec.id}>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Box sx={{ mr: 1 }}>
                            {getRecommendationIcon(rec.type)}
                          </Box>
                          <Typography variant="h6" component="div">
                            {rec.title}
                          </Typography>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {rec.description}
                        </Typography>
                      </CardContent>
                      <CardActions>
                        <Button 
                          size="small" 
                          endIcon={<NavigateNextIcon />} 
                          onClick={rec.action}
                        >
                          Let's Go
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))
              ) : (
                <Grid item xs={12}>
                  <Paper sx={{ p: 2 }}>
                    <Typography color="text.secondary" align="center">
                      Great job! You've been making good progress with your IFS system.
                    </Typography>
                  </Paper>
                </Grid>
              )}
            </Grid>
          </Grid>
          
          {/* Reflective Prompt */}
          <Grid item xs={12}>
            <Paper 
              sx={{ 
                p: 3, 
                mt: 2,
                backgroundColor: 'primary.light', 
                color: 'primary.contrastText',
                position: 'relative'
              }}
            >
              <Typography variant="h6" gutterBottom>
                Reflection For Today
              </Typography>
              <Typography variant="body1" sx={{ fontStyle: 'italic', maxWidth: '80%' }}>
                "{currentPrompt}"
              </Typography>
              <Tooltip title="Get a different prompt">
                <IconButton 
                  onClick={refreshPrompt}
                  sx={{ 
                    position: 'absolute', 
                    top: 8, 
                    right: 8,
                    color: 'primary.contrastText' 
                  }}
                >
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Button 
                variant="contained" 
                sx={{ 
                  mt: 2, 
                  backgroundColor: 'white', 
                  color: 'primary.main',
                  '&:hover': {
                    backgroundColor: 'rgba(255,255,255,0.9)',
                  }
                }}
                onClick={() => navigate('/journal', { 
                  state: { selectedPrompt: currentPrompt } 
                })}
              >
                Journal About This
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Dashboard; 