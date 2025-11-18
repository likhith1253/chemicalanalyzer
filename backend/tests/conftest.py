import pytest
import tempfile
import csv
from io import StringIO
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from equipment.models import Dataset


@pytest.fixture
def api_client():
    """Return an APIClient instance"""
    return APIClient()


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def auth_client(api_client, user):
    """Return an authenticated APIClient"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def sample_csv_content():
    """Return sample CSV content as string"""
    csv_content = StringIO()
    writer = csv.writer(csv_content)
    
    # Write header
    writer.writerow(['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])
    
    # Write sample data
    sample_data = [
        ['Pump-001', 'Pump', '150.5', '2.5', '85.2'],
        ['Valve-A12', 'Valve', '75.3', '1.8', '45.7'],
        ['Reactor-R1', 'Reactor', '200.8', '3.2', '120.5'],
        ['Column-C3', 'Column', '180.2', '2.8', '95.3'],
        ['Pump-002', 'Pump', '165.7', '2.7', '88.9'],
    ]
    
    writer.writerows(sample_data)
    csv_content.seek(0)
    return csv_content.getvalue()


@pytest.fixture
def sample_csv_file(sample_csv_content):
    """Return a temporary CSV file with sample data"""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as f:
        f.write(sample_csv_content)
        f.seek(0)
        return f


@pytest.fixture
def equipment_dataset(user, sample_csv_content):
    """Create a test EquipmentDataset"""
    return Dataset.objects.create(
        name='Test Dataset',
        uploaded_by=user,
        csv_file=tempfile.NamedTemporaryFile(suffix='.csv', delete=False),
        total_count=5,
        avg_flowrate=154.5,
        avg_pressure=2.6,
        avg_temperature=87.12,
        type_distribution={'Pump': 2, 'Valve': 1, 'Reactor': 1, 'Column': 1}
    )


@pytest.fixture
def multiple_datasets(user, sample_csv_content):
    """Create multiple test datasets"""
    datasets = []
    for i in range(3):
        dataset = Dataset.objects.create(
            name=f'Test Dataset {i+1}',
            uploaded_by=user,
            csv_file=tempfile.NamedTemporaryFile(suffix='.csv', delete=False),
            total_count=5,
            avg_flowrate=154.5 + i,
            avg_pressure=2.6 + i * 0.1,
            avg_temperature=87.12 + i,
            type_distribution={'Pump': 2, 'Valve': 1, 'Reactor': 1, 'Column': 1}
        )
        datasets.append(dataset)
    return datasets
