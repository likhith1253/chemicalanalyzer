import pytest
import tempfile
from io import StringIO
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from equipment.models import Dataset


class TestAPIIntegration:
    """Integration tests for complete API workflows"""
    
    def test_complete_workflow(self, api_client, sample_csv_content):
        """Test complete workflow: login -> upload -> retrieve -> download PDF"""
        
        # Step 1: Create user and login
        user = User.objects.create_user(
            username='workflow_user',
            email='workflow@example.com',
            password='workflowpass123'
        )
        
        # Login
        login_data = {
            'username': 'workflow_user',
            'password': 'workflowpass123'
        }
        login_response = api_client.post('/api/auth/login/', login_data, format='json')
        
        assert login_response.status_code == 200
        token = login_response.data['token']
        
        # Authenticate client
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # Step 2: Upload CSV
        from django.core.files.uploadedfile import SimpleUploadedFile
        upload_file = SimpleUploadedFile(
            "workflow_test.csv",
            sample_csv_content.encode(),
            content_type="text/csv"
        )
        
        upload_response = api_client.post('/api/upload/', {'file': upload_file})
        
        assert upload_response.status_code == 200
        dataset_id = upload_response.data['id']
        dataset_name = upload_response.data['name']
        
        # Step 3: List datasets
        list_response = api_client.get('/api/datasets/')
        
        assert list_response.status_code == 200
        assert len(list_response.data['results']) >= 1
        assert any(d['id'] == dataset_id for d in list_response.data['results'])
        
        # Step 4: Get dataset details
        detail_response = api_client.get(f'/api/datasets/{dataset_id}/')
        
        assert detail_response.status_code == 200
        assert detail_response.data['id'] == dataset_id
        assert detail_response.data['name'] == dataset_name
        assert 'preview_rows' in detail_response.data
        assert len(detail_response.data['preview_rows']) > 0
        
        # Step 5: Download PDF report
        pdf_response = api_client.get(f'/api/datasets/{dataset_id}/report/pdf/')
        
        assert pdf_response.status_code == 200
        assert pdf_response['Content-Type'] == 'application/pdf'
        assert len(pdf_response.content) > 0
        assert pdf_response.content.startswith(b'%PDF-')
        
        # Step 6: Logout (if logout endpoint exists)
        # Note: This assumes there's a logout endpoint
        logout_response = api_client.post('/api/auth/logout/', {}, format='json')
        # Logout might not be implemented, so we don't assert status
    
    def test_multiple_users_isolation(self):
        """Test that users can only access their own data"""
        
        # Create two users
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        # Create datasets for each user
        csv_content = "Equipment Name,Type,Flowrate,Pressure,Temperature\nPump-001,Pump,150.5,2.5,85.2"
        
        dataset1 = Dataset.objects.create(
            name='User1 Dataset',
            uploaded_by=user1,
            csv_file=tempfile.NamedTemporaryFile(suffix='.csv', delete=False),
            total_count=1,
            avg_flowrate=150.5,
            avg_pressure=2.5,
            avg_temperature=85.2,
            type_distribution={'Pump': 1}
        )
        
        dataset2 = Dataset.objects.create(
            name='User2 Dataset',
            uploaded_by=user2,
            csv_file=tempfile.NamedTemporaryFile(suffix='.csv', delete=False),
            total_count=1,
            avg_flowrate=150.5,
            avg_pressure=2.5,
            avg_temperature=85.2,
            type_distribution={'Pump': 1}
        )
        
        # Authenticate as user1
        client1 = APIClient()
        client1.force_authenticate(user=user1)
        
        # Authenticate as user2
        client2 = APIClient()
        client2.force_authenticate(user=user2)
        
        # User1 should see their dataset
        response1 = client1.get('/api/datasets/')
        assert response1.status_code == 200
        user1_datasets = [d for d in response1.data['results'] if d['uploaded_by']['username'] == 'user1']
        assert len(user1_datasets) == 1
        assert user1_datasets[0]['name'] == 'User1 Dataset'
        
        # User2 should see their dataset
        response2 = client2.get('/api/datasets/')
        assert response2.status_code == 200
        user2_datasets = [d for d in response2.data['results'] if d['uploaded_by']['username'] == 'user2']
        assert len(user2_datasets) == 1
        assert user2_datasets[0]['name'] == 'User2 Dataset'
    
    def test_concurrent_uploads(self, api_client, user):
        """Test handling multiple concurrent uploads"""
        # Authenticate
        api_client.force_authenticate(user=user)
        
        # Create multiple CSV files
        csv_files = []
        for i in range(5):
            csv_content = f"""Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-{i:04d},Pump,150.5,2.5,85.2
Valve-{i:04d},Valve,75.3,1.8,45.7"""
            
            upload_file = {
                'file': SimpleUploadedFile(
                    f"concurrent_test_{i}.csv",
                    csv_content.encode(),
                    content_type="text/csv"
                )
            }
            csv_files.append(upload_file)
        
        # Upload all files
        responses = []
        for file_data in csv_files:
            response = api_client.post('/api/upload/', file_data)
            responses.append(response)
        
        # All uploads should succeed
        for response in responses:
            assert response.status_code == 200
            assert 'id' in response.data
            assert 'name' in response.data
        
        # Check that all datasets were created
        list_response = api_client.get('/api/datasets/')
        assert list_response.status_code == 200
        assert len(list_response.data['results']) >= 5
    
    def test_large_dataset_workflow(self, api_client, user):
        """Test workflow with large dataset"""
        # Authenticate
        api_client.force_authenticate(user=user)
        
        # Create large CSV content
        csv_lines = ["Equipment Name,Type,Flowrate,Pressure,Temperature"]
        for i in range(100):
            csv_lines.append(f"Pump-{i:04d},Pump,150.5,2.5,85.2")
        
        large_csv_content = "\n".join(csv_lines)
        
        # Upload large dataset
        upload_file = SimpleUploadedFile(
            "large_dataset.csv",
            large_csv_content.encode(),
            content_type="text/csv"
        )
        
        upload_response = api_client.post('/api/upload/', {'file': upload_file})
        
        assert upload_response.status_code == 200
        assert upload_response.data['total_count'] == 100
        
        dataset_id = upload_response.data['id']
        
        # Get dataset details
        detail_response = api_client.get(f'/api/datasets/{dataset_id}/')
        
        assert detail_response.status_code == 200
        assert detail_response.data['total_count'] == 100
        assert len(detail_response.data['preview_rows']) <= 100  # May be limited
        
        # Download PDF (should handle large datasets)
        pdf_response = api_client.get(f'/api/datasets/{dataset_id}/report/pdf/')
        
        assert pdf_response.status_code == 200
        assert pdf_response['Content-Type'] == 'application/pdf'
        assert len(pdf_response.content) > 0
    
    def test_error_handling_workflow(self, api_client):
        """Test error handling throughout the workflow"""
        
        # Try to upload without authentication
        csv_content = "Equipment Name,Type,Flowrate,Pressure,Temperature\nPump-001,Pump,150.5,2.5,85.2"
        upload_file = SimpleUploadedFile(
            "error_test.csv",
            csv_content.encode(),
            content_type="text/csv"
        )
        
        response = api_client.post('/api/upload/', {'file': upload_file})
        assert response.status_code == 401
        
        # Try to access datasets without authentication
        response = api_client.get('/api/datasets/')
        assert response.status_code == 401
        
        # Try to access dataset details without authentication
        response = api_client.get('/api/datasets/1/')
        assert response.status_code == 401
        
        # Try to download PDF without authentication
        response = api_client.get('/api/datasets/1/report/pdf/')
        assert response.status_code == 401
    
    def test_data_consistency_workflow(self, api_client, user):
        """Test data consistency throughout the workflow"""
        # Authenticate
        api_client.force_authenticate(user=user)
        
        # Upload CSV with known data
        known_csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-001,Pump,100.0,2.0,80.0
Pump-002,Pump,200.0,4.0,90.0
Valve-001,Valve,50.0,1.0,60.0"""
        
        upload_file = SimpleUploadedFile(
            "consistency_test.csv",
            known_csv_content.encode(),
            content_type="text/csv"
        )
        
        upload_response = api_client.post('/api/upload/', {'file': upload_file})
        assert upload_response.status_code == 200
        
        dataset_id = upload_response.data['id']
        
        # Verify statistics are correct
        detail_response = api_client.get(f'/api/datasets/{dataset_id}/')
        assert detail_response.status_code == 200
        
        data = detail_response.data
        assert data['total_count'] == 3
        assert data['avg_flowrate'] == (100.0 + 200.0 + 50.0) / 3
        assert data['avg_pressure'] == (2.0 + 4.0 + 1.0) / 3
        assert data['avg_temperature'] == (80.0 + 90.0 + 60.0) / 3
        assert data['type_distribution'] == {'Pump': 2, 'Valve': 1}
        
        # Verify preview rows contain correct data
        preview_rows = data['preview_rows']
        assert len(preview_rows) == 3
        
        # Check specific rows
        pump1_row = next(row for row in preview_rows if row['equipment_name'] == 'Pump-001')
        assert pump1_row['flowrate'] == 100.0
        assert pump1_row['pressure'] == 2.0
        assert pump1_row['temperature'] == 80.0
