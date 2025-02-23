import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider } from './context/AuthContext';
import { IFSProvider } from './context/IFSContext';
import { Dashboard, PartsView, JournalPage, Login, NewPartPage, SystemMapPage } from './pages';
import Navigation from './components/Navigation';
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
        <IFSProvider>
          <Router>
            <div className="App">
              <Navigation />
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/" element={<Dashboard />} />
                <Route path="/parts" element={<PartsView />} />
                <Route path="/parts/new" element={<NewPartPage />} />
                <Route path="/journal" element={<JournalPage />} />
                <Route 
                  path="/system-map" 
                  element={
                    <ErrorBoundary FallbackComponent={ErrorFallback}>
                      <SystemMapPage />
                    </ErrorBoundary>
                  } 
                />
              </Routes>
            </div>
          </Router>
        </IFSProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App; 