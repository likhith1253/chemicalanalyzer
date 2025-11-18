import pytest
from rest_framework.exceptions import ValidationError
from equipment.serializers import DatasetSerializer, DatasetDetailSerializer
from equipment.models import Dataset


class TestDatasetSerializers:
    """Test Dataset serializers"""
    
    def test_dataset_list_serializer(self, equipment_dataset):
        """Test dataset list serializer"""
        serializer = DatasetSerializer(equipment_dataset)
        
        data = serializer.data
        
        assert 'id' in data
        assert 'name' in data
        assert 'uploaded_at' in data
        assert 'total_count' in data
        assert 'uploaded_by' in data
        assert data['uploaded_by']['username'] == 'testuser'
        
        # Should not include detailed fields in list view
        assert 'csv_content' not in data
        assert 'avg_flowrate' not in data
        assert 'avg_pressure' not in data
        assert 'avg_temperature' not in data
        assert 'type_distribution' not in data
        assert 'preview_rows' not in data
    
    def test_dataset_detail_serializer(self, equipment_dataset):
        """Test dataset detail serializer"""
        serializer = EquipmentDatasetDetailSerializer(equipment_dataset)
        
        data = serializer.data
        
        assert 'id' in data
        assert 'name' in data
        assert 'uploaded_at' in data
        assert 'total_count' in data
        assert 'uploaded_by' in data
        assert 'avg_flowrate' in data
        assert 'avg_pressure' in data
        assert 'avg_temperature' in data
        assert 'type_distribution' in data
        assert 'preview_rows' in data
        
        # Check data types
        assert isinstance(data['avg_flowrate'], (int, float))
        assert isinstance(data['avg_pressure'], (int, float))
        assert isinstance(data['avg_temperature'], (int, float))
        assert isinstance(data['type_distribution'], dict)
        assert isinstance(data['preview_rows'], list)
        
        # Should not include raw CSV content
        assert 'csv_content' not in data
    
    def test_dataset_detail_serializer_preview_rows(self, equipment_dataset):
        """Test preview rows in detail serializer"""
        serializer = EquipmentDatasetDetailSerializer(equipment_dataset)
        data = serializer.data
        
        preview_rows = data['preview_rows']
        assert len(preview_rows) == 5
        
        # Check row structure
        row = preview_rows[0]
        assert 'equipment_name' in row
        assert 'type' in row
        assert 'flowrate' in row
        assert 'pressure' in row
        assert 'temperature' in row
        
        # Check data types in rows
        assert isinstance(row['equipment_name'], str)
        assert isinstance(row['type'], str)
        assert isinstance(row['flowrate'], (int, float))
        assert isinstance(row['pressure'], (int, float))
        assert isinstance(row['temperature'], (int, float))
    
    def test_dataset_serializer_validation(self):
        """Test dataset serializer validation"""
        # Test with valid data
        valid_data = {
            'name': 'Test Dataset',
            'csv_content': 'Equipment Name,Type,Flowrate,Pressure,Temperature\nPump-001,Pump,150.5,2.5,85.2',
            'total_count': 1,
            'avg_flowrate': 150.5,
            'avg_pressure': 2.5,
            'avg_temperature': 85.2,
            'type_distribution': {'Pump': 1}
        }
        
        serializer = DatasetSerializer(data=valid_data)
        assert serializer.is_valid()
        
        # Test with missing required fields
        invalid_data = {
            'name': 'Test Dataset'
            # Missing other required fields
        }
        
        serializer = DatasetSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'csv_content' in serializer.errors
        assert 'total_count' in serializer.errors
    
    def test_dataset_serializer_type_distribution_validation(self):
        """Test type distribution field validation"""
        valid_data = {
            'name': 'Test Dataset',
            'csv_content': 'Equipment Name,Type,Flowrate,Pressure,Temperature\nPump-001,Pump,150.5,2.5,85.2',
            'total_count': 1,
            'avg_flowrate': 150.5,
            'avg_pressure': 2.5,
            'avg_temperature': 85.2,
            'type_distribution': {'Pump': 1}
        }
        
        # Test valid type distribution
        serializer = DatasetSerializer(data=valid_data)
        assert serializer.is_valid()
        
        # Test invalid type distribution (not a dict)
        valid_data['type_distribution'] = 'invalid'
        serializer = DatasetSerializer(data=valid_data)
        assert not serializer.is_valid()
        
        # Test invalid type distribution (non-string keys)
        valid_data['type_distribution'] = {1: 1}
        serializer = DatasetSerializer(data=valid_data)
        assert not serializer.is_valid()
        
        # Test invalid type distribution (non-integer values)
        valid_data['type_distribution'] = {'Pump': 'invalid'}
        serializer = DatasetSerializer(data=valid_data)
        assert not serializer.is_valid()
    
    def test_dataset_serializer_numeric_field_validation(self):
        """Test numeric field validation"""
        base_data = {
            'name': 'Test Dataset',
            'csv_content': 'Equipment Name,Type,Flowrate,Pressure,Temperature\nPump-001,Pump,150.5,2.5,85.2',
            'total_count': 1,
            'avg_flowrate': 150.5,
            'avg_pressure': 2.5,
            'avg_temperature': 85.2,
            'type_distribution': {'Pump': 1}
        }
        
        # Test valid numeric fields
        serializer = DatasetSerializer(data=base_data)
        assert serializer.is_valid()
        
        # Test invalid total_count (negative)
        base_data['total_count'] = -1
        serializer = DatasetSerializer(data=base_data)
        assert not serializer.is_valid()
        
        # Test invalid avg_flowrate (string)
        base_data['total_count'] = 1
        base_data['avg_flowrate'] = 'invalid'
        serializer = DatasetSerializer(data=base_data)
        assert not serializer.is_valid()
        
        # Test valid float values
        base_data['avg_flowrate'] = 150.5
        base_data['avg_pressure'] = 2.5
        base_data['avg_temperature'] = 85.2
        serializer = DatasetSerializer(data=base_data)
        assert serializer.is_valid()
    
    def test_dataset_serializer_create(self, user):
        """Test creating dataset through serializer"""
        data = {
            'name': 'Serializer Test',
            'csv_content': 'Equipment Name,Type,Flowrate,Pressure,Temperature\nPump-001,Pump,150.5,2.5,85.2',
            'total_count': 1,
            'avg_flowrate': 150.5,
            'avg_pressure': 2.5,
            'avg_temperature': 85.2,
            'type_distribution': {'Pump': 1}
        }
        
        serializer = DatasetSerializer(data=data)
        assert serializer.is_valid()
        
        # Create dataset (need to set uploaded_by)
        dataset = serializer.save(uploaded_by=user)
        
        assert dataset.name == 'Serializer Test'
        assert dataset.uploaded_by == user
        assert dataset.total_count == 1
        assert dataset.avg_flowrate == 150.5
    
    def test_dataset_serializer_update(self, equipment_dataset):
        """Test updating dataset through serializer"""
        data = {
            'name': 'Updated Name',
            'total_count': 10,
            'avg_flowrate': 200.0,
            'avg_pressure': 3.0,
            'avg_temperature': 100.0,
            'type_distribution': {'Pump': 5, 'Valve': 5}
        }
        
        serializer = DatasetSerializer(equipment_dataset, data=data, partial=True)
        assert serializer.is_valid()
        
        updated_dataset = serializer.save()
        
        assert updated_dataset.name == 'Updated Name'
        assert updated_dataset.total_count == 10
        assert updated_dataset.avg_flowrate == 200.0
        assert updated_dataset.avg_pressure == 3.0
        assert updated_dataset.avg_temperature == 100.0
        assert updated_dataset.type_distribution == {'Pump': 5, 'Valve': 5}
        
        # Other fields should remain unchanged
        assert updated_dataset.uploaded_by == equipment_dataset.uploaded_by
        assert updated_dataset.csv_content == equipment_dataset.csv_content
    
    def test_dataset_serializer_readonly_fields(self, equipment_dataset):
        """Test readonly fields in serializer"""
        # Try to update readonly fields
        data = {
            'id': 999,
            'uploaded_at': '2023-01-01T00:00:00Z',
            'uploaded_by': {'username': 'hacker'},
            'name': 'Updated Name'
        }
        
        serializer = DatasetSerializer(equipment_dataset, data=data, partial=True)
        assert serializer.is_valid()
        
        updated_dataset = serializer.save()
        
        # Readonly fields should not change
        assert updated_dataset.id == equipment_dataset.id
        assert updated_dataset.uploaded_at == equipment_dataset.uploaded_at
        assert updated_dataset.uploaded_by == equipment_dataset.uploaded_by
        
        # Regular fields should update
        assert updated_dataset.name == 'Updated Name'
