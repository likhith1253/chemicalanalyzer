import csv
import io
from typing import List, Dict, Any
from django.core.exceptions import ValidationError


class CSVProcessingError(ValueError):
    """Custom exception for CSV processing errors"""
    pass


class CSVValidationError(ValueError):
    """Custom exception for CSV validation errors"""
    pass


def process_csv_content(csv_content: str) -> List[Dict[str, Any]]:
    """
    Process CSV content and return a list of dictionaries.
    
    Args:
        csv_content: String containing CSV data
        
    Returns:
        List of dictionaries with column headers as keys
        
    Raises:
        ValueError: If CSV format is invalid
    """
    if not csv_content.strip():
        raise CSVValidationError("CSV content is empty")
    
    try:
        # Use StringIO to treat string as file-like object
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        # Check required columns (case-insensitive)
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        actual_columns = [col.strip() for col in reader.fieldnames] if reader.fieldnames else []
        
        # Normalize column names for comparison (case-insensitive, strip whitespace)
        normalized_actual = [col.lower().strip() for col in actual_columns]
        normalized_required = [col.lower().strip() for col in required_columns]
        
        missing_columns = []
        for req_col in normalized_required:
            if req_col not in normalized_actual:
                missing_columns.append(req_col)
        
        if missing_columns:
            raise CSVProcessingError(f"Invalid CSV format: Missing required columns: {', '.join(missing_columns)}")
        
        # Reset file pointer to read data rows
        csv_file.seek(0)
        reader = csv.DictReader(csv_file)
        
        rows = []
        for row_num, row in enumerate(reader, start=1):  # Start at 1 for header row
            if row_num == 1:  # Skip header row
                continue
                
            # Convert numeric fields and normalize column names
            processed_row = {}
            for key, value in row.items():
                # Normalize column names to lowercase with underscores
                normalized_key = key.strip().lower().replace(' ', '_')
                
                if value is not None and str(value).strip():  # Only process non-empty values
                    # Convert numeric fields
                    if normalized_key in ['flowrate', 'pressure', 'temperature']:
                        try:
                            processed_row[normalized_key] = float(str(value).strip())
                        except ValueError:
                            raise CSVProcessingError(f"Invalid data type in row {row_num}")
                    else:
                        processed_row[normalized_key] = str(value).strip()
                else:
                    processed_row[normalized_key] = None
            
            rows.append(processed_row)
        
        return rows
        
    except csv.Error as e:
        raise CSVProcessingError(f"Invalid CSV format: {str(e)}")


def calculate_statistics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics from processed CSV rows.
    
    Args:
        rows: List of dictionaries containing equipment data
        
    Returns:
        Dictionary containing calculated statistics
    """
    if not rows:
        return {
            'total_count': 0,
            'avg_flowrate': 0.0,
            'avg_pressure': 0.0,
            'avg_temperature': 0.0,
            'type_distribution': {}
        }
    
    total_count = len(rows)
    
    # Calculate averages for numeric fields
    flowrates = [row['flowrate'] for row in rows if row.get('flowrate') is not None]
    pressures = [row['pressure'] for row in rows if row.get('pressure') is not None]
    temperatures = [row['temperature'] for row in rows if row.get('temperature') is not None]
    
    avg_flowrate = sum(flowrates) / len(flowrates) if flowrates else 0.0
    avg_pressure = sum(pressures) / len(pressures) if pressures else 0.0
    avg_temperature = sum(temperatures) / len(temperatures) if temperatures else 0.0
    
    # Calculate type distribution
    type_distribution = {}
    for row in rows:
        equipment_type = row.get('type', 'Unknown')
        type_distribution[equipment_type] = type_distribution.get(equipment_type, 0) + 1
    
    return {
        'total_count': total_count,
        'avg_flowrate': round(avg_flowrate, 6),
        'avg_pressure': round(avg_pressure, 6),
        'avg_temperature': round(avg_temperature, 6),
        'type_distribution': type_distribution
    }


def validate_csv_format(csv_content: str) -> None:
    """
    Validate CSV format and required columns.
    
    Args:
        csv_content: String containing CSV data
        
    Raises:
        ValueError: If CSV format is invalid or required columns are missing
    """
    if not csv_content.strip():
        raise CSVValidationError("CSV content is empty")
    
    try:
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        # Check required columns (case-insensitive)
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        actual_columns = [col.strip() for col in reader.fieldnames] if reader.fieldnames else []
        
        # Normalize column names for comparison (case-insensitive, strip whitespace)
        normalized_actual = [col.lower().strip() for col in actual_columns]
        normalized_required = [col.lower().strip() for col in required_columns]
        
        missing_columns = []
        for req_col in normalized_required:
            if req_col not in normalized_actual:
                missing_columns.append(req_col)
        
        if missing_columns:
            raise CSVValidationError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Validate at least one data row
        data_rows = list(reader)
        if not data_rows:
            raise CSVValidationError("CSV must contain at least one data row")
        
        # Validate data types in first few rows
        for i, row in enumerate(data_rows[:5]):  # Check first 5 rows
            row_num = i + 2  # Account for header row
            
            # Check numeric fields
            for field in ['Flowrate', 'Pressure', 'Temperature']:
                value = row.get(field, '').strip()
                if value:  # Only validate if not empty
                    try:
                        float(value)
                    except ValueError:
                        raise CSVValidationError(f"Invalid numeric value for {field} in row {row_num}")
        
    except csv.Error as e:
        raise CSVProcessingError(f"CSV format error: {str(e)}")
