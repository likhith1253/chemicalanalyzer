import pytest
import tempfile
import os
from rest_framework.test import APIClient
from equipment.models import Dataset


class TestPDFReportAPI:
    """Test PDF report generation API endpoint"""
    
    def test_pdf_download_success(self, auth_client, equipment_dataset):
        """Test successful PDF download"""
        response = auth_client.get(f'/api/datasets/{equipment_dataset.id}/report/pdf/')
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
        assert 'attachment' in response['Content-Disposition']
        assert 'pdf' in response['Content-Disposition'].lower()
        
        # Check that response contains PDF content
        assert len(response.content) > 0
        # PDF files start with %PDF-
        assert response.content.startswith(b'%PDF-')
    
    def test_pdf_download_unauthenticated(self, api_client, equipment_dataset):
        """Test PDF download without authentication"""
        response = api_client.get(f'/api/datasets/{equipment_dataset.id}/report/pdf/')
        
        assert response.status_code == 401
    
    def test_pdf_download_not_found(self, auth_client):
        """Test PDF download for non-existent dataset"""
        response = auth_client.get('/api/datasets/99999/report/pdf/')
        
        assert response.status_code == 404
    
    def test_pdf_download_content(self, auth_client, equipment_dataset):
        """Test PDF content contains expected information"""
        response = auth_client.get(f'/api/datasets/{equipment_dataset.id}/report/pdf/')
        
        assert response.status_code == 200
        
        # Save PDF to temporary file for inspection
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_file_path = tmp_file.name
        
        try:
            # Check that file exists and has content
            assert os.path.exists(tmp_file_path)
            assert os.path.getsize(tmp_file_path) > 0
            
            # Basic PDF validation
            with open(tmp_file_path, 'rb') as f:
                content = f.read()
                # PDF should contain dataset name
                assert b'Test Dataset' in content
                # PDF should contain some statistics
                assert b'154.5' in content or b'2.6' in content or b'87.12' in content
                
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    def test_pdf_download_large_dataset(self, auth_client, user):
        """Test PDF download with large dataset"""
        # Create dataset with more data
        large_csv = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-001,Pump,150.5,2.5,85.2
Pump-002,Pump,165.7,2.7,88.9
Pump-003,Pump,142.3,2.3,82.7
Valve-A12,Valve,75.3,1.8,45.7
Valve-B24,Valve,68.9,1.6,42.1
Reactor-R1,Reactor,200.8,3.2,120.5
Reactor-R2,Reactor,210.4,3.5,125.8
Column-C1,Column,175.6,2.6,92.4
Column-C2,Column,190.8,2.9,98.6
Column-C3,Column,180.2,2.8,95.3"""
        
        dataset = EquipmentDataset.objects.create(
            name='Large Dataset',
            uploaded_by=user,
            csv_content=large_csv,
            total_count=10,
            avg_flowrate=156.05,
            avg_pressure=2.59,
            avg_temperature=87.72,
            type_distribution={'Pump': 3, 'Valve': 2, 'Reactor': 2, 'Column': 3}
        )
        
        response = auth_client.get(f'/api/datasets/{dataset.id}/report/pdf/')
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
        assert len(response.content) > 0
        assert response.content.startswith(b'%PDF-')
    
    def test_pdf_download_filename(self, auth_client, equipment_dataset):
        """Test PDF download filename format"""
        response = auth_client.get(f'/api/datasets/{equipment_dataset.id}/report/pdf/')
        
        assert response.status_code == 200
        content_disposition = response['Content-Disposition']
        
        # Check that filename is properly formatted
        assert 'attachment' in content_disposition
        assert 'filename=' in content_disposition
        assert 'pdf' in content_disposition.lower()
        # Should contain dataset name
        assert 'Test Dataset' in content_disposition or 'test_dataset' in content_disposition.lower()
    
    def test_pdf_download_special_characters(self, auth_client, user):
        """Test PDF download with special characters in dataset name"""
        dataset = EquipmentDataset.objects.create(
            name='Test Dataset (Special) & Characters',
            uploaded_by=user,
            csv_content='Equipment Name,Type,Flowrate,Pressure,Temperature\nPump-001,Pump,150.5,2.5,85.2',
            total_count=1,
            avg_flowrate=150.5,
            avg_pressure=2.5,
            avg_temperature=85.2,
            type_distribution={'Pump': 1}
        )
        
        response = auth_client.get(f'/api/datasets/{dataset.id}/report/pdf/')
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
        assert len(response.content) > 0
    
    def test_pdf_download_empty_dataset(self, auth_client, user):
        """Test PDF download with empty dataset"""
        dataset = EquipmentDataset.objects.create(
            name='Empty Dataset',
            uploaded_by=user,
            csv_content='Equipment Name,Type,Flowrate,Pressure,Temperature',
            total_count=0,
            avg_flowrate=0.0,
            avg_pressure=0.0,
            avg_temperature=0.0,
            type_distribution={}
        )
        
        response = auth_client.get(f'/api/datasets/{dataset.id}/report/pdf/')
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
        assert len(response.content) > 0
    
    def test_pdf_download_multiple_requests(self, auth_client, equipment_dataset):
        """Test multiple PDF download requests"""
        # Make multiple requests to ensure consistency
        responses = []
        for i in range(3):
            response = auth_client.get(f'/api/datasets/{equipment_dataset.id}/report/pdf/')
            responses.append(response)
        
        # All responses should be successful
        for response in responses:
            assert response.status_code == 200
            assert response['Content-Type'] == 'application/pdf'
            assert len(response.content) > 0
        
        # Content should be identical
        assert responses[0].content == responses[1].content == responses[2].content
    
    def test_pdf_download_headers(self, auth_client, equipment_dataset):
        """Test PDF download response headers"""
        response = auth_client.get(f'/api/datasets/{equipment_dataset.id}/report/pdf/')
        
        assert response.status_code == 200
        
        # Check important headers
        assert 'Content-Type' in response
        assert response['Content-Type'] == 'application/pdf'
        assert 'Content-Disposition' in response
        assert 'Cache-Control' in response
        
        # Content length should be present
        assert 'Content-Length' in response
        assert int(response['Content-Length']) > 0
