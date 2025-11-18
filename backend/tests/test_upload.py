import pytest
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient


class TestUploadAPI:
    """Test CSV upload API endpoint"""
    
    def test_csv_upload_success(self, auth_client, sample_csv_file):
        """Test successful CSV upload"""
        # Create upload file
        sample_csv_file.seek(0)
        upload_file = SimpleUploadedFile(
            "test.csv",
            sample_csv_file.read().encode(),
            content_type="text/csv"
        )
        
        response = auth_client.post('/api/upload/', {'file': upload_file})
        
        assert response.status_code == 200
        assert 'id' in response.data
        assert 'name' in response.data
        assert 'total_count' in response.data
        assert response.data['total_count'] == 5
        assert 'type_distribution' in response.data
        assert response.data['type_distribution']['Pump'] == 2
        assert response.data['type_distribution']['Valve'] == 1
        assert response.data['type_distribution']['Reactor'] == 1
        assert response.data['type_distribution']['Column'] == 1
    
    def test_csv_upload_unauthenticated(self, api_client, sample_csv_file):
        """Test CSV upload without authentication"""
        sample_csv_file.seek(0)
        upload_file = SimpleUploadedFile(
            "test.csv",
            sample_csv_file.read().encode(),
            content_type="text/csv"
        )
        
        response = api_client.post('/api/upload/', {'file': upload_file})
        
        assert response.status_code == 401
    
    def test_csv_upload_missing_file(self, auth_client):
        """Test CSV upload with missing file"""
        response = auth_client.post('/api/upload/', {})
        
        assert response.status_code == 400
        assert 'file' in response.data
    
    def test_csv_upload_invalid_file_type(self, auth_client):
        """Test CSV upload with invalid file type"""
        upload_file = SimpleUploadedFile(
            "test.txt",
            b"not a csv file",
            content_type="text/plain"
        )
        
        response = auth_client.post('/api/upload/', {'file': upload_file})
        
        assert response.status_code == 400
    
    def test_csv_upload_empty_file(self, auth_client):
        """Test CSV upload with empty file"""
        upload_file = SimpleUploadedFile(
            "empty.csv",
            b"",
            content_type="text/csv"
        )
        
        response = auth_client.post('/api/upload/', {'file': upload_file})
        
        assert response.status_code == 400
    
    def test_csv_upload_invalid_format(self, auth_client):
        """Test CSV upload with invalid CSV format"""
        invalid_csv = "invalid,csv,format\nmissing,columns"
        upload_file = SimpleUploadedFile(
            "invalid.csv",
            invalid_csv.encode(),
            content_type="text/csv"
        )
        
        response = auth_client.post('/api/upload/', {'file': upload_file})
        
        assert response.status_code == 400
    
    def test_csv_upload_missing_columns(self, auth_client):
        """Test CSV upload with missing required columns"""
        invalid_csv = "Name,Type\nPump1,Pump"
        upload_file = SimpleUploadedFile(
            "missing_columns.csv",
            invalid_csv.encode(),
            content_type="text/csv"
        )
        
        response = auth_client.post('/api/upload/', {'file': upload_file})
        
        assert response.status_code == 400
    
    def test_csv_upload_invalid_data_types(self, auth_client):
        """Test CSV upload with invalid data types"""
        invalid_csv = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-001,Pump,not_a_number,2.5,85.2
Valve-A12,Valve,75.3,not_a_number,45.7"""
        
        upload_file = SimpleUploadedFile(
            "invalid_types.csv",
            invalid_csv.encode(),
            content_type="text/csv"
        )
        
        response = auth_client.post('/api/upload/', {'file': upload_file})
        
        assert response.status_code == 400
    
    def test_csv_upload_large_file(self, auth_client):
        """Test CSV upload with large file"""
        # Create a large CSV file (simulated)
        large_csv = "Equipment Name,Type,Flowrate,Pressure,Temperature\n"
        for i in range(10000):
            large_csv += f"Pump-{i:04d},Pump,150.5,2.5,85.2\n"
        
        upload_file = SimpleUploadedFile(
            "large.csv",
            large_csv.encode(),
            content_type="text/csv"
        )
        
        response = auth_client.post('/api/upload/', {'file': upload_file})
        
        assert response.status_code == 200
        assert response.data['total_count'] == 10000
    
    def test_csv_upload_special_characters(self, auth_client):
        """Test CSV upload with special characters in equipment names"""
        special_csv = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-001,Special-Pump,150.5,2.5,85.2
Valve-A12,Valve/Test,75.3,1.8,45.7
Reactor-R1,Reactor & Heater,200.8,3.2,120.5"""
        
        upload_file = SimpleUploadedFile(
            "special_chars.csv",
            special_csv.encode(),
            content_type="text/csv"
        )
        
        response = auth_client.post('/api/upload/', {'file': upload_file})
        
        assert response.status_code == 200
        assert response.data['total_count'] == 3
    
    def test_csv_upload_duplicate_dataset_name(self, auth_client, user, sample_csv_file):
        """Test CSV upload with duplicate dataset name"""
        # Create existing dataset with same name
        from equipment.models import EquipmentDataset
        EquipmentDataset.objects.create(
            name='test.csv',
            uploaded_by=user,
            csv_content='dummy',
            total_count=1,
            avg_flowrate=100.0,
            avg_pressure=2.0,
            avg_temperature=80.0,
            type_distribution={}
        )
        
        sample_csv_file.seek(0)
        upload_file = SimpleUploadedFile(
            "test.csv",
            sample_csv_file.read().encode(),
            content_type="text/csv"
        )
        
        response = auth_client.post('/api/upload/', {'file': upload_file})
        
        assert response.status_code == 200
        # Should create a unique name by adding timestamp
        assert response.data['name'] != 'test.csv'
        assert 'test.csv' in response.data['name']
