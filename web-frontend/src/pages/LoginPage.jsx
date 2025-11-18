import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { authAPI, isAuthenticated } from '../api/client';
import './LoginPage.css';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  
  const navigate = useNavigate();
  const location = useLocation();
  
  // Redirect if already authenticated
  useEffect(() => {
    const checkAuth = () => {
      try {
        if (isAuthenticated()) {
          navigate('/dashboard', { replace: true });
        }
      } catch (error) {
        console.error('Auth check error:', error);
      }
    };
    
    checkAuth();
  }, [navigate]);
  
  // Show registration success message if redirected from register
  useEffect(() => {
    if (location.state?.message) {
      // Message will be shown via toast from API client
      // Clear the state to prevent showing again on refresh
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);
  
  // Get redirect path from location state or default to dashboard
  const from = location.state?.from?.pathname || '/dashboard';

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    }
    
    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    setErrors({});
    
    try {
      const result = await authAPI.login(formData.username, formData.password);
      
      // Check if login was successful
      if (result && result.token) {
        // Small delay to ensure token is stored
        setTimeout(() => {
          navigate('/dashboard', { replace: true });
        }, 100);
      } else {
        throw new Error('Login failed: No token received');
      }
    } catch (error) {
      // Error handling is done in the API client (toast notification)
      console.error('Login error:', error);
      
      // Set form-level error if API returns specific field errors
      if (error.response?.data) {
        const errorData = error.response.data;
        if (errorData.username) {
          setErrors(prev => ({ ...prev, username: Array.isArray(errorData.username) ? errorData.username[0] : errorData.username }));
        }
        if (errorData.password) {
          setErrors(prev => ({ ...prev, password: Array.isArray(errorData.password) ? errorData.password[0] : errorData.password }));
        }
        if (errorData.non_field_errors) {
          setErrors(prev => ({ ...prev, form: Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors[0] : errorData.non_field_errors }));
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <div className="logo">
              <div className="logo-icon">⚗️</div>
              <h1>ChemViz</h1>
            </div>
            <p>Chemical Equipment Parameter Visualizer</p>
          </div>
          
          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className={`form-input ${errors.username ? 'error' : ''}`}
                placeholder="Enter your username"
                disabled={isLoading}
              />
              {errors.username && <span className="error-message">{errors.username}</span>}
            </div>
            
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={`form-input ${errors.password ? 'error' : ''}`}
                placeholder="Enter your password"
                disabled={isLoading}
              />
              {errors.password && <span className="error-message">{errors.password}</span>}
            </div>
            
            {errors.form && (
              <div className="error-message" style={{ marginBottom: '15px', textAlign: 'center' }}>
                {errors.form}
              </div>
            )}
            
            <button
              type="submit"
              className="login-button"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="loading-spinner"></div>
              ) : (
                'Sign In'
              )}
            </button>
          </form>
          
          <div className="login-footer">
            <p>
              Don't have an account?{' '}
              <Link to="/register" className="register-link">
                Register here
              </Link>
            </p>
          </div>
        </div>
        
        <div className="login-background">
          <div className="floating-elements">
            <div className="element element-1">🧪</div>
            <div className="element element-2">⚗️</div>
            <div className="element element-3">🔬</div>
            <div className="element element-4">💧</div>
            <div className="element element-5">🧫</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
