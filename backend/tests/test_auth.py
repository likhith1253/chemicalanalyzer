import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


class TestAuthenticationAPI:
    """Test authentication API endpoints"""
    
    def test_login_success(self, api_client, user):
        """Test successful login"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == 200
        assert 'token' in response.data
        assert response.data['token'] is not None
        
        # Verify token was created for user
        token = Token.objects.get(user=user)
        assert response.data['token'] == token.key
    
    def test_login_invalid_credentials(self, api_client):
        """Test login with invalid credentials"""
        data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == 401
        assert 'token' not in response.data
    
    def test_login_missing_fields(self, api_client):
        """Test login with missing fields"""
        # Missing password
        data = {'username': 'testuser'}
        response = api_client.post('/api/auth/login/', data, format='json')
        assert response.status_code == 400
        
        # Missing username
        data = {'password': 'testpass123'}
        response = api_client.post('/api/auth/login/', data, format='json')
        assert response.status_code == 400
        
        # Missing both
        data = {}
        response = api_client.post('/api/auth/login/', data, format='json')
        assert response.status_code == 400
    
    def test_login_nonexistent_user(self, api_client):
        """Test login with non-existent user"""
        data = {
            'username': 'nonexistent',
            'password': 'somepass'
        }
        
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == 401
        assert 'token' not in response.data
    
    def test_token_authentication(self, auth_client, user):
        """Test token-based authentication"""
        # Get user info with authenticated client
        response = auth_client.get('/api/datasets/')
        
        assert response.status_code == 200
        assert 'results' in response.data
    
    def test_unauthenticated_access(self, api_client):
        """Test access without authentication"""
        # Try to access protected endpoint without token
        response = api_client.get('/api/datasets/')
        
        assert response.status_code == 401
    
    def test_invalid_token(self, api_client):
        """Test access with invalid token"""
        # Set invalid token
        api_client.credentials(HTTP_AUTHORIZATION='Token invalidtoken123')
        
        response = api_client.get('/api/datasets/')
        
        assert response.status_code == 401
    
    def test_token_creation_on_login(self, api_client, user):
        """Test that token is created on first login"""
        # Ensure user has no token initially
        assert not Token.objects.filter(user=user).exists()
        
        # Login
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = api_client.post('/api/auth/login/', data, format='json')
        
        assert response.status_code == 200
        assert Token.objects.filter(user=user).exists()
        
        # Login again should return same token
        token_key = response.data['token']
        response2 = api_client.post('/api/auth/login/', data, format='json')
        assert response2.status_code == 200
        assert response2.data['token'] == token_key
