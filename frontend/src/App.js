import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider } from './context/AuthContext';
import { IFSProvider } from './context/IFSContext';
import { 
  Dashboard, 
  PartsView, 
  JournalPage, 
  Login, 
  Register,
  NewPartPage, 
  SystemMapPage, 
  PartDetailsPage 
} from './pages';
import { Navigation, ProtectedRoute } from './components';
import { ErrorBoundary } from 'react-error-boundary';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#f50057',
    },
  },
});

function ErrorFallback({error}) {
  return (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
    </div>
  )
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <div className="App">
            <Navigation />
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Protected routes */}
              <Route path="/" element={
                <ProtectedRoute>
                  <IFSProvider>
                    <Dashboard />
                  </IFSProvider>
                </ProtectedRoute>
              } />
              <Route path="/parts" element={
                <ProtectedRoute>
                  <IFSProvider>
                    <PartsView />
                  </IFSProvider>
                </ProtectedRoute>
              } />
              <Route path="/parts/new" element={
                <ProtectedRoute>
                  <IFSProvider>
                    <NewPartPage />
                  </IFSProvider>
                </ProtectedRoute>
              } />
              <Route path="/journal" element={
                <ProtectedRoute>
                  <IFSProvider>
                    <JournalPage />
                  </IFSProvider>
                </ProtectedRoute>
              } />
              <Route path="/system-map" element={
                <ProtectedRoute>
                  <IFSProvider>
                    <ErrorBoundary FallbackComponent={ErrorFallback}>
                      <SystemMapPage />
                    </ErrorBoundary>
                  </IFSProvider>
                </ProtectedRoute>
              } />
              <Route path="/parts/:partId" element={
                <ProtectedRoute>
                  <IFSProvider>
                    <PartDetailsPage />
                  </IFSProvider>
                </ProtectedRoute>
              } />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App; 