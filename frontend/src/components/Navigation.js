import React from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  useMediaQuery,
  useTheme,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { useAuth } from '../context/AuthContext';

const Navigation = () => {
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [logoutDialogOpen, setLogoutDialogOpen] = React.useState(false);
  const { currentUser, logout } = useAuth();
  
  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleLogoutClick = () => {
    setLogoutDialogOpen(true);
  };

  const handleLogoutCancel = () => {
    setLogoutDialogOpen(false);
  };

  const handleLogoutConfirm = () => {
    setLogoutDialogOpen(false);
    logout();
    if (anchorEl) {
      handleMenuClose();
    }
  };
  
  const isActive = (path) => location.pathname === path;
  
  const navItems = currentUser ? [
    { label: 'Dashboard', path: '/' },
    { label: 'Parts', path: '/parts' },
    { label: 'System Map', path: '/system-map' },
    { label: 'Journal', path: '/journal' },
  ] : [];
  
  return (
    <AppBar position="static">
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{
              mr: 2,
              fontWeight: 700,
              color: 'white',
              textDecoration: 'none',
            }}
          >
            IFS Explorer
          </Typography>
          
          <Box sx={{ flexGrow: 1 }} />
          
          {currentUser ? (
            <>
              {isMobile ? (
                <>
                  <IconButton
                    color="inherit"
                    aria-label="menu"
                    onClick={handleMenuClick}
                    edge="start"
                  >
                    <MenuIcon />
                  </IconButton>
                  <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleMenuClose}
                  >
                    {navItems.map((item) => (
                      <MenuItem
                        key={item.path}
                        component={RouterLink}
                        to={item.path}
                        onClick={handleMenuClose}
                        selected={isActive(item.path)}
                      >
                        {item.label}
                      </MenuItem>
                    ))}
                    <MenuItem onClick={handleLogoutClick}>
                      Logout
                    </MenuItem>
                  </Menu>
                </>
              ) : (
                <>
                  <Box sx={{ display: 'flex' }}>
                    {navItems.map((item) => (
                      <Button
                        key={item.path}
                        component={RouterLink}
                        to={item.path}
                        sx={{
                          mx: 1,
                          color: 'white',
                          fontWeight: isActive(item.path) ? 'bold' : 'normal',
                          borderBottom: isActive(item.path) ? '2px solid white' : 'none',
                        }}
                      >
                        {item.label}
                      </Button>
                    ))}
                  </Box>
                  <Button 
                    color="inherit" 
                    onClick={handleLogoutClick}
                    sx={{ ml: 2 }}
                  >
                    Logout
                  </Button>
                </>
              )}
              
              {/* Logout Confirmation Dialog */}
              <Dialog
                open={logoutDialogOpen}
                onClose={handleLogoutCancel}
                aria-labelledby="logout-dialog-title"
                aria-describedby="logout-dialog-description"
              >
                <DialogTitle id="logout-dialog-title">
                  Confirm Logout
                </DialogTitle>
                <DialogContent>
                  <DialogContentText id="logout-dialog-description">
                    Are you sure you want to log out?
                  </DialogContentText>
                </DialogContent>
                <DialogActions>
                  <Button onClick={handleLogoutCancel} color="primary">
                    Cancel
                  </Button>
                  <Button onClick={handleLogoutConfirm} color="primary" autoFocus>
                    Logout
                  </Button>
                </DialogActions>
              </Dialog>
            </>
          ) : (
            <>
              {!isActive('/login') && (
                <Button
                  color="inherit"
                  component={RouterLink}
                  to="/login"
                >
                  Login
                </Button>
              )}
              {!isActive('/register') && (
                <Button
                  color="inherit"
                  component={RouterLink}
                  to="/register"
                >
                  Register
                </Button>
              )}
            </>
          )}
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navigation; 