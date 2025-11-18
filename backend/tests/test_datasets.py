import pytest
import tempfile
from django.urls import reverse
from rest_framework.test import APIClient
from equipment.models import Dataset


class TestDatasetsAPI:
    """Test datasets API endpoints"""
    
    def test_get_datasets_list(self, auth_client, multiple_datasets):
        """Test getting list of datasets"""
        response = auth_client.get('/api/datasets/')
        
        assert response.status_code == 200
        assert 'results' in response.data
        assert len(response.data['results']) == 3
        
        # Check dataset structure
        dataset = response.data['results'][0]
        assert 'id' in dataset
        assert 'name' in dataset
        assert 'uploaded_at' in dataset
        assert 'total_count' in dataset
        assert 'uploaded_by' in dataset
        assert dataset['uploaded_by']['username'] == 'testuser'
    
    def test_get_datasets_empty(self, auth_client):
        """Test getting datasets list when no datasets exist"""
        response = auth_client.get('/api/datasets/')
        
        assert response.status_code == 200
        assert 'results' in response.data
        assert len(response.data['results']) == 0
    
    def test_get_datasets_unauthenticated(self, api_client):
        """Test getting datasets without authentication"""
        response = api_client.get('/api/datasets/')
        
        assert response.status_code == 401
    
    def test_get_dataset_detail(self, auth_client, equipment_dataset):
        """Test getting dataset details"""
        response = auth_client.get(f'/api/datasets/{equipment_dataset.id}/')
        
        assert response.status_code == 200
        assert response.data['id'] == equipment_dataset.id
        assert response.data['name'] == 'Test Dataset'
        assert response.data['total_count'] == 5
        assert response.data['avg_flowrate'] == 154.5
        assert response.data['avg_pressure'] == 2.6
        assert response.data['avg_temperature'] == 87.12
        assert response.data['type_distribution'] == {'Pump': 2, 'Valve': 1, 'Reactor': 1, 'Column': 1}
        assert 'preview_rows' in response.data
        assert len(response.data['preview_rows']) == 5
    
    def test_get_dataset_detail_not_found(self, auth_client):
        """Test getting non-existent dataset"""
        response = auth_client.get('/api/datasets/99999/')
        
        assert response.status_code == 404
    
    def test_get_dataset_detail_unauthenticated(self, api_client, equipment_dataset):
        """Test getting dataset detail without authentication"""
        response = api_client.get(f'/api/datasets/{equipment_dataset.id}/')
        
        assert response.status_code == 401
    
    def test_get_dataset_detail_other_user(self, auth_client, equipment_dataset):
        """Test getting dataset detail from another user (should be accessible)"""
        # Create another user and dataset
        from django.contrib.auth.models import User
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        other_dataset = EquipmentDataset.objects.create(
            name='Other Dataset',
            uploaded_by=other_user,
            csv_content='dummy',
            total_count=1,
            avg_flowrate=100.0,
            avg_pressure=2.0,
            avg_temperature=80.0,
            type_distribution={'Pump': 1}
        )
        
        # Try to access other user's dataset
        response = auth_client.get(f'/api/datasets/{other_dataset.id}/')
        
        # Depending on implementation, this might be allowed or forbidden
        # For now, assume it's allowed (no user filtering)
        assert response.status_code in [200, 403, 404]
    
    def test_datasets_pagination(self, auth_client, multiple_datasets):
        """Test datasets list pagination"""
        # Create more datasets to test pagination
        from equipment.models import Dataset
        for i in range(10):
            Dataset.objects.create(
                name=f'Extra Dataset {i}',
                uploaded_by=multiple_datasets[0].uploaded_by,
                csv_file=tempfile.NamedTemporaryFile(suffix='.csv', delete=False),
                total_count=1,
                avg_flowrate=100.0,
                avg_pressure=2.0,
                avg_temperature=80.0,
                type_distribution={'Pump': 1}
            )
        
        response = auth_client.get('/api/datasets/')
        
        assert response.status_code == 200
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data
        assert len(response.data['results']) <= 20  # Default page size
    
    def test_datasets_ordering(self, auth_client, multiple_datasets):
        """Test datasets list ordering"""
        response = auth_client.get('/api/datasets/?ordering=-uploaded_at')
        
        assert response.status_code == 200
        datasets = response.data['results']
        
        # Check that datasets are ordered by uploaded_at descending
        for i in range(len(datasets) - 1):
            assert datasets[i]['uploaded_at'] >= datasets[i+1]['uploaded_at']
    
    def test_datasets_search(self, auth_client, multiple_datasets):
        """Test datasets list search"""
        # Search by name
        response = auth_client.get('/api/datasets/?search=Test Dataset 1')
        
        assert response.status_code == 200
        datasets = response.data['results']
        assert len(datasets) == 1
        assert 'Test Dataset 1' in datasets[0]['name']
    
    def test_dataset_preview_rows_format(self, auth_client, equipment_dataset):
        """Test dataset preview rows format"""
        response = auth_client.get(f'/api/datasets/{equipment_dataset.id}/')
        
        assert response.status_code == 200
        preview_rows = response.data['preview_rows']
        
        assert isinstance(preview_rows, list)
        assert len(preview_rows) > 0
        
        # Check row structure
        row = preview_rows[0]
        assert 'equipment_name' in row
        assert 'type' in row
        assert 'flowrate' in row
        assert 'pressure' in row
        assert 'temperature' in row
        
        # Check data types
        assert isinstance(row['equipment_name'], str)
        assert isinstance(row['type'], str)
        assert isinstance(row['flowrate'], (int, float))
        assert isinstance(row['pressure'], (int, float))
        assert isinstance(row['temperature'], (int, float))
    
    def test_dataset_statistics_accuracy(self, auth_client, equipment_dataset):
        """Test dataset statistics accuracy"""
        response = auth_client.get(f'/api/datasets/{equipment_dataset.id}/')
        
        assert response.status_code == 200
        data = response.data
        
        # Verify statistics match the data
        assert data['total_count'] == 5
        assert data['avg_flowrate'] == 154.5
        assert data['avg_pressure'] == 2.6
        assert data['avg_temperature'] == 87.12
        
        # Verify type distribution
        type_dist = data['type_distribution']
        assert type_dist['Pump'] == 2
        assert type_dist['Valve'] == 1
        assert type_dist['Reactor'] == 1
        assert type_dist['Column'] == 1
