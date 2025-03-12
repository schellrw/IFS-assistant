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
import DonutLargeIcon from '@mui/icons-material/DonutLarge';
import BarChartIcon from '@mui/icons-material/BarChart';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import { format, formatDistanceToNow, differenceInDays } from 'date-fns';
import { useIFS } from '../context/IFSContext';
import { REFLECTIVE_PROMPTS } from '../constants';
import { PartsDistributionChart, EmotionsChart, MiniSystemMap } from '../components';
import axios from 'axios';

// Configure API base URL - can be changed via environment variable later
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const Dashboard = () => {
  const { system, loading: ifsLoading, error: ifsError, journals, getJournals, isAuthenticated } = useIFS();
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

  // Effect to fetch recent activity and generate recommendations
  useEffect(() => {
    let isMounted = true;
    
    const fetchData = async () => {
      if (loadingActivity || !isMounted) return;
      
      setLoadingActivity(true);
      
      try {
        // Only try to fetch journals if we don't have any and we have a system
        let journalData = [];
        if (journals.length === 0 && system && system.id) {
          try {
            journalData = await getJournals();
          } catch (err) {
            console.error('Error loading journals:', err);
            journalData = [];
          }
        } else {
          journalData = journals;
        }
        
        if (!isMounted) return;
        
        // Create combined activity list
        const allActivity = [];
        
        // Add journal entries to activity
        if (journalData && journalData.length > 0) {
          journalData.slice(0, 5).forEach(journal => {
            if (journal && journal.id) {
              allActivity.push({
                type: 'journal',
                id: journal.id,
                title: journal.title || 'Untitled Journal',
                timestamp: new Date(journal.date),
                associatedId: journal.part_id
              });
            }
          });
        }
        
        // Add parts to activity (if available)
        if (system && system.parts) {
          Object.values(system.parts).forEach(part => {
            allActivity.push({
              type: 'part',
              id: part.id,
              title: `Part created: "${part.name}"`,
              timestamp: new Date(part.created_at || Date.now()),
              associatedId: part.id
            });
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
          
        if (isMounted) {
          setRecentActivity(sortedActivity);
          
          // Generate personalized recommendations
          const newRecommendations = [];
          
          // Add recommendations based on system state
          const partsCount = system && system.parts ? Object.keys(system.parts).length : 0;
          
          if (partsCount === 0) {
            newRecommendations.push({
              type: 'parts',
              title: 'Identify Your First Part',
              description: 'Start by identifying your first internal part to begin mapping your system.',
              action: 'Create Part',
              path: '/parts/new'
            });
          } else if (partsCount < 3) {
            newRecommendations.push({
              type: 'parts',
              title: 'Add More Parts',
              description: 'Continue identifying internal parts to better understand your system.',
              action: 'Create Part',
              path: '/parts/new'
            });
          }
          
          // Journal recommendations
          const journalsCount = journalData.length;
          
          if (journalsCount === 0) {
            newRecommendations.push({
              type: 'journal',
              title: 'Start Your Journal',
              description: 'Record your first journal entry to track your IFS journey.',
              action: 'New Journal',
              path: '/journal'
            });
          } else if (journalsCount < 5) {
            newRecommendations.push({
              type: 'journal',
              title: 'Continue Journaling',
              description: 'Regular journaling helps track progress and gain insights.',
              action: 'New Journal',
              path: '/journal'
            });
          }
          
          // Relationship recommendations if we have multiple parts
          if (partsCount >= 2 && (!system.relationships || Object.keys(system.relationships).length === 0)) {
            newRecommendations.push({
              type: 'relationship',
              title: 'Map Relationships',
              description: 'Start connecting parts to understand how they interact with each other.',
              action: 'Add Relationship',
              path: '/relationships'
            });
          }
          
          // Additional recommendations
          newRecommendations.push({
            type: 'visualization',
            title: 'Visualize Your System',
            description: 'See a visual representation of your internal family system.',
            action: 'View Map',
            path: '/map'
          });
          
          // Shuffle and select 3 recommendations
          const shuffled = newRecommendations.sort(() => 0.5 - Math.random());
          setRecommendations(shuffled.slice(0, 3));
        }
      } catch (err) {
        console.error('Error in dashboard data loading:', err);
        if (isMounted) {
          setRecentActivity([]);
        }
      } finally {
        if (isMounted) {
          setLoadingActivity(false);
        }
      }
    };
    
    if (isAuthenticated && system) {
      fetchData();
    }
    
    return () => {
      isMounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, system, journals.length, loadingActivity]);

  const handleActivityClick = (type, id) => {
    if (type === 'journal') {
      navigate('/journal', { 
        state: { 
          highlightId: id,
          selectedPrompt: currentPrompt 
        } 
      });
    } else if (type === 'part_created' || type === 'part_updated') {
      navigate(`/parts/${id}`, { state: { from: 'dashboard' } });
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
          <Grid item xs={12} md={4}>
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
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, height: '100%' }}>
              <Typography variant="h6" gutterBottom>Recent Activity</Typography>
              
              {loadingActivity ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : recentActivity.length > 0 ? (
                <List dense sx={{ maxHeight: 300, overflow: 'auto' }}>
                  {recentActivity.map((activity, index) => (
                    <React.Fragment key={activity.id}>
                      {index > 0 && <Divider variant="inset" component="li" />}
                      <ListItem 
                        alignItems="flex-start"
                        onClick={() => handleActivityClick(activity.type, activity.associatedId)}
                        sx={{ cursor: 'pointer' }}
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
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Personalized Recommendations
              </Typography>
              
              {ifsLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : recommendations.length > 0 ? (
                <Box>
                  {recommendations.map(recommendation => (
                    <Card key={recommendation.id} sx={{ mb: 2 }}>
                      <CardContent sx={{ pb: 0 }}>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                          <Box sx={{ mr: 1, pt: 0.5 }}>
                            {getRecommendationIcon(recommendation.type)}
                          </Box>
                          <Box>
                            <Typography variant="h6" component="div">
                              {recommendation.title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {recommendation.description}
                            </Typography>
                          </Box>
                        </Box>
                      </CardContent>
                      <CardActions>
                        <Button 
                          size="small" 
                          endIcon={<NavigateNextIcon />}
                          onClick={() => navigate(recommendation.path)}
                        >
                          {recommendation.action}
                        </Button>
                      </CardActions>
                    </Card>
                  ))}
                </Box>
              ) : (
                <Typography color="text.secondary" align="center">
                  No recommendations at this time.
                </Typography>
              )}
            </Paper>
          </Grid>
          
          {/* Second row: Visualizations */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2, mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" gutterBottom sx={{ mb: 0 }}>
                  System Visualizations
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => navigate('/system-map')}
                  startIcon={<AccountTreeIcon />}
                >
                  Full System Map
                </Button>
              </Box>
              
              {ifsLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                  <CircularProgress />
                </Box>
              ) : system && Object.keys(system.parts).length > 0 ? (
                <Grid container spacing={3}>
                  {/* Parts Distribution Chart */}
                  <Grid item xs={12} md={4}>
                    <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <DonutLargeIcon color="primary" sx={{ mr: 1 }} />
                        <Typography variant="subtitle1">Parts by Role</Typography>
                      </Box>
                      <PartsDistributionChart 
                        parts={system ? Object.values(system.parts) : []} 
                        height={220} 
                      />
                    </Paper>
                  </Grid>
                  
                  {/* Emotions Chart */}
                  <Grid item xs={12} md={4}>
                    <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <BarChartIcon color="primary" sx={{ mr: 1 }} />
                        <Typography variant="subtitle1">Emotions Across Parts</Typography>
                      </Box>
                      <EmotionsChart 
                        parts={system ? Object.values(system.parts) : []} 
                        height={220} 
                      />
                    </Paper>
                  </Grid>
                  
                  {/* Mini System Map */}
                  <Grid item xs={12} md={4}>
                    <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <AccountTreeIcon color="primary" sx={{ mr: 1 }} />
                        <Typography variant="subtitle1">Mini System Map</Typography>
                      </Box>
                      <MiniSystemMap 
                        parts={system ? Object.values(system.parts) : []}
                        relationships={system ? Object.values(system.relationships) : []}
                        height={220}
                        maxNodes={8}
                      />
                    </Paper>
                  </Grid>
                </Grid>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography color="text.secondary" paragraph>
                    Add parts to your system to see visualizations
                  </Typography>
                  <Button
                    variant="contained"
                    onClick={() => navigate('/parts/new')}
                  >
                    Add Your First Part
                  </Button>
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Reflection for Today */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3, borderRadius: 2, bgcolor: 'primary.main', color: 'white' }}>
              <Typography variant="h6" gutterBottom>
                Reflection for Today
              </Typography>
              <Typography variant="body1" sx={{ fontStyle: 'italic', maxWidth: '80%' }}>
                {currentPrompt}
              </Typography>
              <Box sx={{ display: 'flex', mt: 2 }}>
                <Button 
                  variant="text" 
                  color="inherit" 
                  size="small"
                  onClick={refreshPrompt}
                  sx={{ mr: 2 }}
                  startIcon={<RefreshIcon />}
                >
                  New Prompt
                </Button>
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
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Dashboard; 