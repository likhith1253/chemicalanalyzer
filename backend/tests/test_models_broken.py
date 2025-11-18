import pytest
import tempfile
import os
from django.core.files import File
from django.contrib.auth.models import User
from equipment.models import Dataset


class TestDatasetModel:
    """Test Dataset model"""
    
    def test_create_dataset(self, user, sample_csv_content):
        """Test creating a dataset"""
        # Create a proper temporary file for csv_file field
        import tempfile
        from django.core.files import File
        
        # Create a temporary file with a proper name
        temp_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False, prefix='test_dataset_')
        temp_file.write(sample_csv_content)
        temp_file.seek(0)  # Reset file pointer
        
        # Create Django File object
        django_file = File(temp_file)
        
        dataset = Dataset.objects.create(
            name='Test Dataset',
            uploaded_by=user,
            csv_file=django_file,
            total_count=5,
            avg_flowrate=154.5,
            avg_pressure=2.6,
            avg_temperature=87.12,
            type_distribution={'Pump': 2, 'Valve': 1, 'Reactor': 1, 'Column': 1}
        )
        
        assert dataset.name == 'Test Dataset'
        assert dataset.uploaded_by == user
        assert dataset.total_count == 5
        assert dataset.avg_flowrate == 154.5
        assert dataset.avg_pressure == 2.6
        assert dataset.avg_temperature == 87.12
        assert dataset.type_distribution == {'Pump': 2, 'Valve': 1, 'Reactor': 1, 'Column': 1}
        assert dataset.uploaded_at is not None
        
        # Clean up temporary file
        temp_file.close()
        import os
        os.unlink(temp_file.name)
    
    def test_dataset_str_method(self, user):
        """Test dataset string representation"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_file.write(b'dummy')
        temp_file.seek(0)
        
        dataset = Dataset.objects.create(
            name='Test Dataset',
            uploaded_by=user,
            csv_file=File(temp_file),
            total_count=1,
            avg_flowrate=100.0,
            avg_pressure=2.0,
            avg_temperature=80.0,
            type_distribution={'Pump': 1}
        )
        
        expected_str = f"Test Dataset - {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
        assert str(dataset) == expected_str
        
        temp_file.close()
        os.unlink(temp_file.name)
    
    def test_dataset_ordering(self, user):
        """Test dataset default ordering"""
        # Create datasets with different timestamps
        temp_file1 = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_file1.write(b'dummy1')
        temp_file1.seek(0)
        
        dataset1 = Dataset.objects.create(
            name='Dataset 1',
            uploaded_by=user,
            csv_file=File(temp_file1),
            total_count=1,
            avg_flowrate=100.0,
            avg_pressure=2.0,
            avg_temperature=80.0,
            type_distribution={'Pump': 1}
        )
        
        temp_file2 = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_file2.write(b'dummy2')
        temp_file2.seek(0)
        
        dataset2 = Dataset.objects.create(
            name='Dataset 2',
            uploaded_by=user,
            csv_file=File(temp_file2),
            total_count=1,
            avg_flowrate=100.0,
            avg_pressure=2.0,
            avg_temperature=80.0,
            type_distribution={'Pump': 1}
        )
        
        # Get all datasets - should be ordered by uploaded_at descending
        datasets = Dataset.objects.all()
        assert datasets[0] == dataset2  # More recent
        assert datasets[1] == dataset1  # Older
        
        temp_file1.close()
        temp_file2.close()
        os.unlink(temp_file1.name)
        os.unlink(temp_file2.name)
    
    def test_dataset_json_fields(self, user):
        """Test JSON field handling"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_file.write(b'dummy')
        temp_file.seek(0)
        
        dataset = Dataset.objects.create(
            name='JSON Test',
            uploaded_by=user,
            csv_file=File(temp_file),
            total_count=1,
            avg_flowrate=100.0,
            avg_pressure=2.0,
            avg_temperature=80.0,
            type_distribution={'Pump': 2, 'Valve': 3, 'Reactor': 1}
        )
        
        # Test retrieval
        retrieved = Dataset.objects.get(id=dataset.id)
        assert retrieved.type_distribution == {'Pump': 2, 'Valve': 3, 'Reactor': 1}
        
        # Test updating
        retrieved.type_distribution = {'Column': 5}
        retrieved.save()
        
        updated = Dataset.objects.get(id=dataset.id)
        assert updated.type_distribution == {'Column': 5}
        
        temp_file.close()
        os.unlink(temp_file.name)
    
    def test_dataset_csv_content_storage(self, user, sample_csv_content):
        """Test CSV content storage and retrieval"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_file.write(sample_csv_content.encode('utf-8'))
        temp_file.seek(0)
        
        dataset = Dataset.objects.create(
            name='CSV Content Test',
            uploaded_by=user,
            csv_file=File(temp_file),
            total_count=5,
            avg_flowrate=154.5,
            avg_pressure=2.6,
            avg_temperature=87.12,
            type_distribution={'Pump': 2, 'Valve': 1, 'Reactor': 1, 'Column': 1}
        )
        
        # Test content storage
        retrieved = Dataset.objects.get(id=dataset.id)
        # Note: csv_file is stored as FileField, not as string content
        assert retrieved.name == 'CSV Content Test'
        
        temp_file.close()
        os.unlink(temp_file.name)
    
    def test_dataset_validation(self, user):
        """Test dataset field validation"""
        # Test required fields
        with pytest.raises(Exception):  # Should raise IntegrityError or similar
            Dataset.objects.create(
                # Missing name
                uploaded_by=user,
                csv_file=File(tempfile.NamedTemporaryFile(suffix='.csv', delete=False)),
                total_count=1,
                avg_flowrate=100.0,
                avg_pressure=2.0,
                avg_temperature=80.0,
                type_distribution={'Pump': 1}
            )
        
        with pytest.raises(Exception):  # Should raise IntegrityError or similar
            Dataset.objects.create(
                name='Test',
                # Missing uploaded_by
                csv_file=File(tempfile.NamedTemporaryFile(suffix='.csv', delete=False)),
                total_count=1,
                avg_flowrate=100.0,
                avg_pressure=2.0,
                avg_temperature=80.0,
                type_distribution={'Pump': 1}
            )
    
    def test_dataset_unique_name_per_user(self, user):
        """Test dataset name uniqueness per user"""
        temp_file1 = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_file1.write(b'dummy1')
        temp_file1.seek(0)
        
        Dataset.objects.create(
            name='Same Name',
            uploaded_by=user,
            csv_file=File(temp_file1),
            total_count=1,
            avg_flowrate=100.0,
            avg_pressure=2.0,
            avg_temperature=80.0,
            type_distribution={'Pump': 1}
        )
        
        # Should be able to create another dataset with same name for different user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        temp_file2 = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_file2.write(b'dummy2')
        temp_file2.seek(0)
        
        other_dataset = Dataset.objects.create(
            name='Same Name',
            uploaded_by=other_user,
            csv_file=File(temp_file2),
            total_count=1,
            avg_flowrate=100.0,
            avg_pressure=2.0,
            avg_temperature=80.0,
            type_distribution={'Pump': 1}
        )
        
        assert other_dataset.uploaded_by == other_user
        assert other_dataset.name == 'Same Name'
        
        temp_file1.close()
        temp_file2.close()
        os.unlink(temp_file1.name)
        os.unlink(temp_file2.name)
    
    def test_dataset_soft_delete_behavior(self, user):
        """Test dataset behavior after deletion"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_file.write(b'dummy')
        temp_file.seek(0)
        
        dataset = Dataset.objects.create(
            name='To Delete',
            uploaded_by=user,
            csv_file=File(temp_file),
            total_count=1,
            avg_flowrate=100.0,
            avg_pressure=2.0,
            avg_temperature=80.0,
            type_distribution={'Pump': 1}
        )
        
        dataset_id = dataset.id
        dataset.delete()
        
        # Dataset should be deleted
        assert not Dataset.objects.filter(id=dataset_id).exists()
        
        temp_file.close()
        os.unlink(temp_file.name)
    
    def test_dataset_bulk_operations(self, user):
        """Test bulk operations on datasets"""
        datasets = []
        temp_files = []
        
        for i in range(5):
            temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
            temp_file.write(f'dummy{i}'.encode('utf-8'))
            temp_file.seek(0)
            temp_files.append(temp_file)
            
            dataset = Dataset.objects.create(
                name=f'Bulk Dataset {i}',
                uploaded_by=user,
                csv_file=File(temp_file),
                total_count=1,
                avg_flowrate=100.0 + i,
                avg_pressure=2.0 + i * 0.1,
                avg_temperature=80.0 + i,
                type_distribution={'Pump': 1}
            )
            datasets.append(dataset)
        
        # Test bulk update
        Dataset.objects.filter(id__in=[d.id for d in datasets]).update(
            avg_flowrate=200.0
        )
        
        updated_datasets = Dataset.objects.filter(id__in=[d.id for d in datasets])
        for dataset in updated_datasets:
            assert dataset.avg_flowrate == 200.0
        
        # Test bulk delete
        deleted_count, _ = Dataset.objects.filter(id__in=[d.id for d in datasets]).delete()
        assert deleted_count == 5
        
        # Clean up temp files
        for temp_file in temp_files:
            temp_file.close()
            os.unlink(temp_file.name)
