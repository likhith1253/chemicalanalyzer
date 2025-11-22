import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance with base URL from environment
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle authentication errors
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      sessionStorage.removeItem('auth_token');
      window.location.href = '/login';
      toast.error('Session expired. Please login again.');
    }
    
    // Handle other common errors
    if (error.response?.status === 403) {
      toast.error('Access denied. You do not have permission to perform this action.');
    }
    
    if (error.response?.status === 404) {
      toast.error('Resource not found.');
    }
    
    if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    }
    
    // Network errors
    if (error.code === 'ECONNABORTED') {
      toast.error('Request timeout. Please try again.');
    }
    
    if (error.code === 'ERR_NETWORK') {
      toast.error('Network error. Please check your connection.');
    }
    
    return Promise.reject(error);
  }
);

// API functions
export const authAPI = {
  login: async (username, password) => {
    try {
      const response = await apiClient.post('/auth/login/', {
        username,
        password,
      });
      
      // Backend returns EXACTLY: { token, username }
      const responseData = response.data || {};
      const token = responseData.token;
      const username = responseData.username;
      
      if (!token) {
        throw new Error('No token received from server');
      }
      
      // Store token in localStorage
      sessionStorage.setItem('auth_token', token);
      
      // Store user object with username
      const user = { username: username };
      sessionStorage.setItem('user', JSON.stringify(user));
      
      toast.success('Login successful!');
      return { token, user };
    } catch (error) {
      // Extract error message from various possible locations
      const errorData = error.response?.data || {};
      const errorMessage = errorData.detail || 
                          errorData.error || 
                          errorData.message ||
                          (errorData.non_field_errors && Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors[0] : errorData.non_field_errors) ||
                          'Login failed. Please check your credentials.';
      
      toast.error(errorMessage);
      throw error;
    }
  },
  
  register: async (username, email, password, passwordConfirm) => {
    try {
      const response = await apiClient.post('/auth/register/', {
        username,
        email: email || '',
        password,
        password_confirm: passwordConfirm,
      });
      
      const responseData = response.data || {};
      
      // If registration returns a token, store it (some APIs do this)
      if (responseData.token) {
        sessionStorage.setItem('auth_token', responseData.token);
        if (responseData.user) {
          sessionStorage.setItem('user', JSON.stringify(responseData.user));
        }
      }
      
      toast.success('Registration successful! Please login.');
      return responseData;
    } catch (error) {
      // Extract error message from various possible locations
      const errorData = error.response?.data || {};
      const errorMessage = errorData.detail || 
                          errorData.error || 
                          errorData.message ||
                          (errorData.non_field_errors && Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors[0] : errorData.non_field_errors) ||
                          'Registration failed. Please try again.';
      
      toast.error(errorMessage);
      throw error;
    }
  },
  
  logout: async () => {
    try {
      await apiClient.post('/auth/logout/');
    } catch (error) {
      // Even if logout fails on server, clear local storage
      console.error('Logout error:', error);
    } finally {
      // Clear local storage
      sessionStorage.removeItem('auth_token');
      sessionStorage.removeItem('user');
      toast.success('Logged out successfully');
    }
  },
  
  getProfile: async () => {
    try {
      const response = await apiClient.get('/auth/profile/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export const datasetAPI = {
  // Upload CSV file
  uploadCsv: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post('/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 seconds for file upload
      });
      
      // Backend returns data directly: { id, name, total_count, avg_flowrate, preview_rows, ... }
      const responseData = response.data || {};
      
      toast.success('File uploaded and analyzed successfully!');
      return responseData;
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'File upload failed. Please try again.';
      toast.error(errorMessage);
      throw error;
    }
  },
  
  // Get list of datasets (last 5)
  fetchDatasets: async () => {
    try {
      const response = await apiClient.get('/datasets/');
      // Backend returns array directly: [{ id, name, total_count, ... }, ...]
      const data = response.data || [];
      return Array.isArray(data) ? data : [];
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'Failed to fetch datasets.';
      toast.error(errorMessage);
      throw error;
    }
  },
  
  // Get dataset details
  fetchDatasetDetail: async (id) => {
    try {
      const response = await apiClient.get(`/datasets/${id}/`);
      // Backend returns data directly: { id, name, total_count, preview_rows, ... }
      return response.data || {};
    } catch (error) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'Failed to fetch dataset details.';
      toast.error(errorMessage);
      throw error;
    }
  },
  
  // Download PDF report
  downloadPdfReport: async (id) => {
    try {
      const response = await apiClient.get(`/datasets/${id}/report/pdf/`, {
        responseType: 'blob',
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `dataset_${id}_report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('PDF report downloaded successfully!');
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to download PDF report.';
      toast.error(errorMessage);
      throw error;
    }
  },

  // Generate AI insights
  analyzeDataset: async (id) => {
    try {
      const response = await apiClient.get(`/datasets/${id}/analyze/`);
      return response.data || {};
    } catch (error) {
      // Don't show toast for service unavailable errors - let component handle it
      if (error.response?.status !== 503) {
        const errorMessage = error.response?.data?.detail || error.response?.data?.error || 'Failed to generate AI insights.';
        toast.error(errorMessage);
      }
      throw error;
    }
  },
};

// Helper function to check if user is authenticated
export const isAuthenticated = () => {
  const token = sessionStorage.getItem('auth_token');
  return !!token;
};

// Helper function to get current user
export const getCurrentUser = () => {
  const userStr = sessionStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

// Helper function to clear auth data
export const clearAuthData = () => {
  sessionStorage.removeItem('auth_token');
  sessionStorage.removeItem('user');
};

export default apiClient;
