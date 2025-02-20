import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, Grid, Card, CardContent, 
  CardActions, Button, Box 
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useIFS } from '../context/IFSContext';

const PartsView = () => {
  const { system } = useIFS();
  const navigate = useNavigate();
  const [parts, setParts] = useState([]);

  useEffect(() => {
    if (system?.parts) {
      setParts(Object.values(system.parts));
    }
  }, [system]);

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Parts
          </Typography>
          <Button 
            variant="contained" 
            color="primary"
            onClick={() => navigate('/new-part')}
          >
            Add New Part
          </Button>
        </Box>

        <Grid container spacing={3}>
          {parts.map((part) => (
            <Grid item xs={12} sm={6} md={4} key={part.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{part.name}</Typography>
                  <Typography color="textSecondary" gutterBottom>
                    {part.role || 'Undefined Role'}
                  </Typography>
                  <Typography variant="body2" noWrap>
                    {part.description}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button 
                    size="small" 
                    onClick={() => navigate(`/parts/${part.id}`)}
                  >
                    View Details
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
};

export default PartsView; 