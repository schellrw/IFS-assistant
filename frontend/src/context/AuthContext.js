import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Add debug logging
console.log(`Using API base URL: ${API_BASE_URL}`);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [detailedError, setDetailedError] = useState(null);

  // Set axios default headers when token changes
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem('token', token);
      console.log('Token set in localStorage and axios headers:', token.substring(0, 10) + '...');
    } else {
      delete axios.defaults.headers.common['Authorization'];
      localStorage.removeItem('token');
      console.log('Token removed from localStorage and axios headers');
    }
  }, [token]);

  // Initial auth check using token from localStorage
  useEffect(() => {
    const initialToken = localStorage.getItem('token');
    if (initialToken && initialToken !== 'undefined' && initialToken !== 'null') {
      console.log('Found token in localStorage:', initialToken.substring(0, 10) + '...');
      setToken(initialToken);
    } else {
      console.log('No valid token found in localStorage');
      setToken(null);
    }
    setLoading(false);
  }, []);

  // Check if there's a stored token on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          console.log('Checking stored token validity...');
          const response = await axios.get(`${API_BASE_URL}/api/system`);
          console.log('Token is valid, user authenticated');
          setCurrentUser({
            id: response.data.user_id,
            username: 'User' // You might want to fetch user details in a production app
          });
        } catch (err) {
          console.error('Auth token invalid:', err);
          console.error('Response data:', err.response?.data);
          console.error('Status code:', err.response?.status);
          setToken(null);
          setDetailedError({
            message: 'Token validation failed',
            status: err.response?.status,
            data: err.response?.data,
            error: err.message
          });
        }
      } else {
        console.log('No token found, user not authenticated');
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  const register = async (username, email, password) => {
    setLoading(true);
    setError('');
    setDetailedError(null);
    try {
      console.log('Attempting registration with:', { username, email });
      const response = await axios.post(`${API_BASE_URL}/api/register`, {
        username,
        email,
        password
      });
      console.log('Registration response:', response.data);
      setToken(response.data.access_token);
      setCurrentUser(response.data.user);
      return response.data;
    } catch (err) {
      console.error('Registration error details:', err.response?.data || err.message);
      const message = err.response?.data?.error || 'Registration failed';
      setError(message);
      setDetailedError({
        message: message,
        status: err.response?.status,
        data: err.response?.data,
        error: err.message
      });
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    setLoading(true);
    setError('');
    setDetailedError(null);
    try {
      console.log(`Attempting login for user: ${username} to ${API_BASE_URL}/api/login`);
      const response = await axios.post(`${API_BASE_URL}/api/login`, {
        username,
        password
      });
      console.log('Login successful, response:', response.data);
      
      if (!response.data.access_token) {
        throw new Error('No access token received from server');
      }
      
      // Save token and set current user
      const receivedToken = response.data.access_token;
      setToken(receivedToken);
      setCurrentUser(response.data.user);
      
      // Double-check token was set
      console.log(`Token saved: ${receivedToken.substring(0, 10)}...`);
      
      return response.data;
    } catch (err) {
      console.error('Login failed with error:', err);
      console.error('Response status:', err.response?.status);
      console.error('Response data:', err.response?.data);
      
      const message = err.response?.data?.error || 'Login failed';
      setError(message);
      setDetailedError({
        message: message,
        status: err.response?.status,
        data: err.response?.data,
        error: err.message
      });
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    console.log('Logging out user');
    setToken(null);
    setCurrentUser(null);
  };

  const value = {
    token,
    setToken,
    currentUser,
    loading,
    error,
    detailedError,
    login,
    logout,
    register,
    isAuthenticated: !!token
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 