import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List


class APIClient:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"
        
        self.config_path = Path(config_path)
        self.base_url = None
        self.timeout = 30
        self.token = None
        self.session = requests.Session()
        
        self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.base_url = config.get('api', {}).get('base_url', 'http://localhost:8000/api')
                self.timeout = config.get('api', {}).get('timeout', 30)
        except FileNotFoundError:
            # Default configuration if file doesn't exist
            self.base_url = 'http://localhost:8000/api'
            self.timeout = 30
            print(f"Warning: Config file {self.config_path} not found. Using default settings.")
        except json.JSONDecodeError:
            self.base_url = 'http://localhost:8000/api'
            self.timeout = 30
            print(f"Warning: Invalid JSON in {self.config_path}. Using default settings.")
    
    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        if include_auth and self.token:
            headers['Authorization'] = f'Token {self.token}'
        
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception("Authentication failed. Please check your credentials.")
            elif response.status_code == 403:
                raise Exception("Access forbidden. You don't have permission to perform this action.")
            elif response.status_code == 404:
                raise Exception("Resource not found.")
            elif response.status_code >= 500:
                raise Exception("Server error. Please try again later.")
            else:
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        raise Exception(error_data['detail'])
                    elif 'error' in error_data:
                        raise Exception(error_data['error'])
                    else:
                        raise Exception(f"HTTP {response.status_code}: {response.text}")
                except json.JSONDecodeError:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Invalid response format from server.")
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login to the API and store token"""
        url = f"{self.base_url}/auth/login/"
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(url, json=data, headers=self._get_headers(include_auth=False))
            result = self._handle_response(response)
            
            if 'token' in result:
                self.token = result['token']
                return result
            else:
                raise Exception("No token received from server")
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")
    
    def logout(self):
        """Logout and clear token"""
        self.token = None
        # Note: Django REST Framework doesn't have a logout endpoint for token auth
        # Token will be invalidated on the server side if needed
    
    def upload_csv(self, file_path: str) -> Dict[str, Any]:
        """Upload CSV file to the API"""
        if not self.token:
            raise Exception("Authentication required. Please login first.")
        
        url = f"{self.base_url}/upload/"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                headers = {}  # Don't set Content-Type for multipart/form-data
                if self.token:
                    headers['Authorization'] = f'Token {self.token}'
                
                response = self.session.post(url, files=files, headers=headers, timeout=self.timeout)
                return self._handle_response(response)
        except FileNotFoundError:
            raise Exception(f"File not found: {file_path}")
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")
    
    def get_datasets(self) -> List[Dict[str, Any]]:
        """Get list of datasets"""
        if not self.token:
            raise Exception("Authentication required. Please login first.")
        
        url = f"{self.base_url}/datasets/"
        
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=self.timeout)
            result = self._handle_response(response)
            
            # Handle paginated response
            if isinstance(result, dict) and 'results' in result:
                return result['results']
            elif isinstance(result, list):
                return result
            else:
                raise Exception("Unexpected response format")
        except Exception as e:
            raise Exception(f"Failed to fetch datasets: {str(e)}")
    
    def get_dataset_detail(self, dataset_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific dataset"""
        if not self.token:
            raise Exception("Authentication required. Please login first.")
        
        url = f"{self.base_url}/datasets/{dataset_id}/"
        
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            raise Exception(f"Failed to fetch dataset detail: {str(e)}")
    def get_ai_insights(self, dataset_id: int) -> str:
        """Get AI insights for a dataset"""
        if not self.token:
            raise Exception("Authentication required. Please login first.")
        
        url = f"{self.base_url}/datasets/{dataset_id}/analyze/"
        
        try:
            headers = {'Authorization': f'Token {self.token}'}
            response = self.session.get(url, headers=headers, timeout=60) # Longer timeout for AI
            result = self._handle_response(response)
            return result.get('insights', 'No insights generated.')
        except Exception as e:
            raise Exception(f"Failed to generate AI insights: {str(e)}")
        """Download PDF report for a dataset"""
        if not self.token:
            raise Exception("Authentication required. Please login first.")
        
        url = f"{self.base_url}/datasets/{dataset_id}/report/pdf/"
        
        try:
            headers = {'Authorization': f'Token {self.token}'}
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Save PDF to file
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise Exception("PDF report not found for this dataset.")
            else:
                raise Exception(f"Failed to download PDF: {str(e)}")
        except Exception as e:
            raise Exception(f"PDF download failed: {str(e)}")
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.token is not None
    
    def get_base_url(self) -> str:
        """Get current base URL"""
        return self.base_url
    
    def set_base_url(self, base_url: str):
        """Set base URL"""
        self.base_url = base_url.rstrip('/')
    
    def get_timeout(self) -> int:
        """Get current timeout setting"""
        return self.timeout
    
    def set_timeout(self, timeout: int):
        """Set timeout setting"""
        self.timeout = timeout


# Global API client instance
api_client = APIClient()
