import pytest
import tempfile
import csv
from io import StringIO
from equipment.utils import process_csv_content, calculate_statistics, validate_csv_format


class TestCSVProcessingUtils:
    """Test CSV processing utility functions"""
    
    def test_process_csv_content_valid(self):
        """Test processing valid CSV content"""
        csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-001,Pump,150.5,2.5,85.2
Valve-A12,Valve,75.3,1.8,45.7
Reactor-R1,Reactor,200.8,3.2,120.5"""
        
        rows = process_csv_content(csv_content)
        
        assert len(rows) == 3
        assert rows[0]['equipment_name'] == 'Pump-001'
        assert rows[0]['type'] == 'Pump'
        assert rows[0]['flowrate'] == 150.5
        assert rows[0]['pressure'] == 2.5
        assert rows[0]['temperature'] == 85.2
    
    def test_process_csv_content_empty(self):
        """Test processing empty CSV content"""
        csv_content = ""
        
        with pytest.raises(ValueError, match="CSV content is empty"):
            process_csv_content(csv_content)
    
    def test_process_csv_content_headers_only(self):
        """Test processing CSV with headers only"""
        csv_content = "Equipment Name,Type,Flowrate,Pressure,Temperature"
        
        rows = process_csv_content(csv_content)
        
        assert len(rows) == 0
    
    def test_process_csv_content_invalid_format(self):
        """Test processing CSV with invalid format"""
        csv_content = "invalid,csv,format\nmissing,columns"
        
        with pytest.raises(ValueError, match="Invalid CSV format"):
            process_csv_content(csv_content)
    
    def test_process_csv_content_missing_columns(self):
        """Test processing CSV with missing required columns"""
        csv_content = "Name,Type\nPump-001,Pump"
        
        with pytest.raises(ValueError, match="Missing required columns"):
            process_csv_content(csv_content)
    
    def test_process_csv_content_invalid_data_types(self):
        """Test processing CSV with invalid data types"""
        csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-001,Pump,not_a_number,2.5,85.2"""
        
        with pytest.raises(ValueError, match="Invalid data type"):
            process_csv_content(csv_content)
    
    def test_process_csv_content_special_characters(self):
        """Test processing CSV with special characters"""
        csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-001,Special-Pump,150.5,2.5,85.2
Valve-A12,Valve/Test,75.3,1.8,45.7"""
        
        rows = process_csv_content(csv_content)
        
        assert len(rows) == 2
        assert rows[0]['type'] == 'Special-Pump'
        assert rows[1]['type'] == 'Valve/Test'
    
    def test_calculate_statistics_empty(self):
        """Test calculating statistics for empty data"""
        stats = calculate_statistics([])
        
        assert stats['total_count'] == 0
        assert stats['avg_flowrate'] == 0.0
        assert stats['avg_pressure'] == 0.0
        assert stats['avg_temperature'] == 0.0
        assert stats['type_distribution'] == {}
    
    def test_calculate_statistics_single_row(self):
        """Test calculating statistics for single row"""
        rows = [{
            'equipment_name': 'Pump-001',
            'type': 'Pump',
            'flowrate': 150.5,
            'pressure': 2.5,
            'temperature': 85.2
        }]
        
        stats = calculate_statistics(rows)
        
        assert stats['total_count'] == 1
        assert stats['avg_flowrate'] == 150.5
        assert stats['avg_pressure'] == 2.5
        assert stats['avg_temperature'] == 85.2
        assert stats['type_distribution'] == {'Pump': 1}
    
    def test_calculate_statistics_multiple_rows(self):
        """Test calculating statistics for multiple rows"""
        rows = [
            {'equipment_name': 'Pump-001', 'type': 'Pump', 'flowrate': 150.5, 'pressure': 2.5, 'temperature': 85.2},
            {'equipment_name': 'Pump-002', 'type': 'Pump', 'flowrate': 165.7, 'pressure': 2.7, 'temperature': 88.9},
            {'equipment_name': 'Valve-A12', 'type': 'Valve', 'flowrate': 75.3, 'pressure': 1.8, 'temperature': 45.7},
            {'equipment_name': 'Reactor-R1', 'type': 'Reactor', 'flowrate': 200.8, 'pressure': 3.2, 'temperature': 120.5}
        ]
        
        stats = calculate_statistics(rows)
        
        assert stats['total_count'] == 4
        assert stats['avg_flowrate'] == (150.5 + 165.7 + 75.3 + 200.8) / 4
        assert stats['avg_pressure'] == (2.5 + 2.7 + 1.8 + 3.2) / 4
        assert stats['avg_temperature'] == (85.2 + 88.9 + 45.7 + 120.5) / 4
        assert stats['type_distribution'] == {'Pump': 2, 'Valve': 1, 'Reactor': 1}
    
    def test_calculate_statistics_precision(self):
        """Test statistics calculation precision"""
        rows = [
            {'equipment_name': 'Test-1', 'type': 'Test', 'flowrate': 1.333333, 'pressure': 2.666666, 'temperature': 3.999999}
        ]
        
        stats = calculate_statistics(rows)
        
        assert stats['avg_flowrate'] == 1.333333
        assert stats['avg_pressure'] == 2.666666
        assert stats['avg_temperature'] == 3.999999
    
    def test_validate_csv_format_valid(self):
        """Test validating valid CSV format"""
        csv_content = "Equipment Name,Type,Flowrate,Pressure,Temperature\nPump-001,Pump,150.5,2.5,85.2"
        
        # Should not raise any exception
        validate_csv_format(csv_content)
    
    def test_validate_csv_format_empty(self):
        """Test validating empty CSV format"""
        csv_content = ""
        
        with pytest.raises(ValueError, match="CSV content is empty"):
            validate_csv_format(csv_content)
    
    def test_validate_csv_format_invalid_headers(self):
        """Test validating CSV with invalid headers"""
        csv_content = "Name,Type,Flowrate\nPump-001,Pump,150.5"
        
        with pytest.raises(ValueError, match="Missing required columns"):
            validate_csv_format(csv_content)
    
    def test_validate_csv_format_case_insensitive(self):
        """Test CSV format validation is case insensitive"""
        csv_content = "equipment name,type,flowrate,pressure,temperature\nPump-001,Pump,150.5,2.5,85.2"
        
        # Should not raise any exception
        validate_csv_format(csv_content)
    
    def test_validate_csv_format_extra_whitespace(self):
        """Test CSV format validation with extra whitespace"""
        csv_content = "  Equipment Name , Type , Flowrate , Pressure , Temperature  \nPump-001,Pump,150.5,2.5,85.2"
        
        # Should not raise any exception
        validate_csv_format(csv_content)
    
    def test_validate_csv_format_different_order(self):
        """Test CSV format validation with different column order"""
        csv_content = "Type,Equipment Name,Flowrate,Pressure,Temperature\nPump,Pump-001,150.5,2.5,85.2"
        
        # Should not raise any exception
        validate_csv_format(csv_content)
    
    def test_process_large_csv(self):
        """Test processing large CSV file"""
        # Generate large CSV content
        csv_lines = ["Equipment Name,Type,Flowrate,Pressure,Temperature"]
        for i in range(1000):
            csv_lines.append(f"Pump-{i:04d},Pump,150.5,2.5,85.2")
        
        csv_content = "\n".join(csv_lines)
        
        rows = process_csv_content(csv_content)
        
        assert len(rows) == 1000
        assert rows[0]['equipment_name'] == 'Pump-0000'
        assert rows[-1]['equipment_name'] == 'Pump-0999'
    
    def test_calculate_statistics_large_dataset(self):
        """Test calculating statistics for large dataset"""
        # Generate large dataset
        rows = []
        for i in range(1000):
            rows.append({
                'equipment_name': f'Pump-{i:04d}',
                'type': 'Pump',
                'flowrate': 150.5 + i * 0.01,
                'pressure': 2.5 + i * 0.001,
                'temperature': 85.2 + i * 0.01
            })
        
        stats = calculate_statistics(rows)
        
        assert stats['total_count'] == 1000
        assert stats['type_distribution'] == {'Pump': 1000}
        assert abs(stats['avg_flowrate'] - (150.5 + 999 * 0.01 / 2)) < 0.01
