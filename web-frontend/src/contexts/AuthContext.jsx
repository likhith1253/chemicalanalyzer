import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI, getCurrentUser, isAuthenticated as checkAuthToken } from '../api/client';

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
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      try {
        // Check if we have a token locally
        if (checkAuthToken()) {
          // Optimistically set user from local storage if available
          const storedUser = getCurrentUser();
          if (storedUser) {
            setUser(storedUser);
            setIsAuthenticated(true);
          }

          // Verify with backend to ensure token is valid
          try {
            const profile = await authAPI.getProfile();
            setUser(profile);
            setIsAuthenticated(true);
          } catch (error) {
            // Token is invalid or expired
            console.warn('Session verification failed:', error);
            setUser(null);
            setIsAuthenticated(false);
            // Optional: Clear invalid token
            // localStorage.removeItem('auth_token'); 
            // We let the interceptor handle strict 401s, but here we just update state
          }
        } else {
          setUser(null);
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password);

      const userData = response.user;
      setUser(userData);
      setIsAuthenticated(true);

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

  const register = async (username, email, password, passwordConfirm) => {
    try {
      const response = await authAPI.register(username, email, password, passwordConfirm);

      // If registration returns a token (auto-login)
      if (response.token) {
        const userData = response.user;
        setUser(userData);
        setIsAuthenticated(true);
        return { success: true, user: userData, token: response.token };
      }

      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail ||
        error.response?.data?.error ||
        error.message ||
        'Registration failed';
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
      setIsAuthenticated(false);
    }
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    isAuthenticated,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
