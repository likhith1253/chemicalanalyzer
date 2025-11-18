import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI, getCurrentUser, isAuthenticated } from '../api/client';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated on mount
    if (isAuthenticated()) {
      const currentUser = getCurrentUser();
      if (currentUser) {
        setUser(currentUser);
      }
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password);
      
      // Get user data from response or localStorage
      const userData = response?.user || getCurrentUser();
      
      if (userData) {
        setUser(userData);
      } else {
        // If no user in response, try to get from localStorage
        const storedUser = getCurrentUser();
        if (storedUser) {
          setUser(storedUser);
        }
      }
      
      return { success: true, user: userData };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.error || 
                          error.message || 
                          'Login failed';
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
    }
  };

  const value = {
    user,
    login,
    logout,
    loading,
    isAuthenticated: isAuthenticated(),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
