import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const IFSContext = createContext();

export const useIFS = () => useContext(IFSContext);

export const IFSProvider = ({ children }) => {
    // ... IFSProvider implementation from ifs-frontend.js ...
}; 