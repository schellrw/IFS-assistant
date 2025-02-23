import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const IFSContext = createContext();

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const useIFS = () => {
  const context = useContext(IFSContext);
  if (!context) {
    throw new Error('useIFS must be used within an IFSProvider');
  }
  return context;
};

export const IFSProvider = ({ children }) => {
  const [system, setSystem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSystem();
  }, []);

  const fetchSystem = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/system`);
      setSystem(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch system data');
      console.error('Error fetching system:', err);
    } finally {
      setLoading(false);
    }
  };

  const addPart = async (partData) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/parts`, partData);
      await fetchSystem(); // Refresh system data
      return response.data;
    } catch (err) {
      console.error('Error adding part:', err);
      throw err;
    }
  };

  const updatePart = async (partId, updates) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/api/parts/${partId}`, updates);
      await fetchSystem(); // Refresh system data
      return response.data;
    } catch (err) {
      console.error('Error updating part:', err);
      throw err;
    }
  };

  const addJournal = async (journalData) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/journals`, journalData);
      await fetchSystem(); // Refresh system data
      return response.data;
    } catch (err) {
      console.error('Error adding journal entry:', err);
      throw err;
    }
  };

  const addRelationship = async (relationshipData) => {
    try {
      console.log('IFSContext: Sending relationship data:', relationshipData);
      const response = await axios.post(`${API_BASE_URL}/api/relationships`, relationshipData);
      console.log('IFSContext: Server response:', response.data);
      await fetchSystem(); // Refresh system data
      return response.data;
    } catch (err) {
      console.error('IFSContext: Error adding relationship:', err.response?.data || err);
      throw new Error(err.response?.data?.error || err.message);
    }
  };

  const updateRelationship = async (relationshipId, updates) => {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/api/relationships/${relationshipId}`, 
        updates
      );
      await fetchSystem();
      return response.data;
    } catch (err) {
      console.error('Error updating relationship:', err);
      throw err;
    }
  };

  const deleteRelationship = async (relationshipId) => {
    try {
      await axios.delete(`${API_BASE_URL}/api/relationships/${relationshipId}`);
      await fetchSystem();
    } catch (err) {
      console.error('Error deleting relationship:', err);
      throw err;
    }
  };

  const deletePart = async (partId) => {
    try {
      await axios.delete(`${API_BASE_URL}/api/parts/${partId}`);
      await fetchSystem(); // Refresh system data
    } catch (err) {
      console.error('Error deleting part:', err);
      throw err;
    }
  };

  const value = {
    system,
    loading,
    error,
    fetchSystem,
    addPart,
    updatePart,
    addJournal,
    addRelationship,
    updateRelationship,
    deleteRelationship,
    deletePart
  };

  return (
    <IFSContext.Provider value={value}>
      {children}
    </IFSContext.Provider>
  );
}; 