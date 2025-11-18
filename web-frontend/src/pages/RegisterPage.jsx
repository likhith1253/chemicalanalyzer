import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI, isAuthenticated } from '../api/client';
import './LoginPage.css';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    passwordConfirm: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  
  const navigate = useNavigate();
  
  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated()) {
      navigate('/dashboard', { replace: true });
    }
  }, [navigate]);

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
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }
    
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    
    if (!formData.passwordConfirm.trim()) {
      newErrors.passwordConfirm = 'Please confirm your password';
    } else if (formData.password !== formData.passwordConfirm) {
      newErrors.passwordConfirm = 'Passwords do not match';
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
      await authAPI.register(
        formData.username,
        formData.email,
        formData.password,
        formData.passwordConfirm
      );
      // Redirect to login page after successful registration
      // Small delay to ensure toast is shown
      setTimeout(() => {
        navigate('/login', { 
          replace: true,
          state: { message: 'Registration successful! Please login.' }
        });
      }, 500);
    } catch (error) {
      // Error handling is done in the API client
      console.error('Registration error:', error);
      // Set form-level error if needed
      if (error.response?.data) {
        const errorData = error.response.data;
        if (errorData.username) {
          setErrors(prev => ({ ...prev, username: errorData.username[0] }));
        }
        if (errorData.email) {
          setErrors(prev => ({ ...prev, email: errorData.email[0] }));
        }
        if (errorData.password) {
          setErrors(prev => ({ ...prev, password: errorData.password[0] }));
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
            <p>Create your account</p>
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
                autoComplete="username"
              />
              {errors.username && <span className="error-message">{errors.username}</span>}
            </div>
            
            <div className="form-group">
              <label htmlFor="email">Email (Optional)</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={`form-input ${errors.email ? 'error' : ''}`}
                placeholder="Enter your email"
                disabled={isLoading}
                autoComplete="email"
              />
              {errors.email && <span className="error-message">{errors.email}</span>}
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
                placeholder="Enter your password (min 8 characters)"
                disabled={isLoading}
                autoComplete="new-password"
              />
              {errors.password && <span className="error-message">{errors.password}</span>}
            </div>
            
            <div className="form-group">
              <label htmlFor="passwordConfirm">Confirm Password</label>
              <input
                type="password"
                id="passwordConfirm"
                name="passwordConfirm"
                value={formData.passwordConfirm}
                onChange={handleChange}
                className={`form-input ${errors.passwordConfirm ? 'error' : ''}`}
                placeholder="Confirm your password"
                disabled={isLoading}
                autoComplete="new-password"
              />
              {errors.passwordConfirm && <span className="error-message">{errors.passwordConfirm}</span>}
            </div>
            
            <button
              type="submit"
              className="login-button"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="loading-spinner"></div>
              ) : (
                'Create Account'
              )}
            </button>
          </form>
          
          <div className="login-footer">
            <p>
              Already have an account?{' '}
              <Link to="/login" className="register-link">
                Sign in here
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

export default RegisterPage;

