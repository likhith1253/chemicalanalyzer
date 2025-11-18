import pandas as pd
import re
from typing import Dict, List, Optional, Union
from django.core.files.uploadedfile import UploadedFile


class CSVParsingError(Exception):
    """Custom exception for CSV parsing errors."""
    pass


def normalize_column_name(column_name: str) -> str:
    """
    Normalize column names to standard format.
    Accepts exact column names: "Equipment Name", "Type", "Flowrate", "Pressure", "Temperature"
    
    Args:
        column_name: Original column name from CSV
        
    Returns:
        Normalized column name (lowercase with underscores)
    """
    # Strip whitespace and convert to string
    original = str(column_name).strip()
    
    # Direct mapping for exact column names (case-insensitive)
    exact_mapping = {
        'equipment name': 'equipment_name',
        'equipmentname': 'equipment_name',
        'type': 'type',
        'flowrate': 'flowrate',
        'pressure': 'pressure',
        'temperature': 'temperature',
    }
    
    # Check exact match first (case-insensitive)
    lower_original = original.lower().strip()
    if lower_original in exact_mapping:
        return exact_mapping[lower_original]
    
    # Convert to lowercase, strip whitespace, replace spaces with underscores
    normalized = lower_original.replace(' ', '_')
    
    # Remove special characters except underscores
    normalized = re.sub(r'[^a-z0-9_]', '', normalized)
    
    # Map common variations to standard names
    column_mapping = {
        'equipment_name': 'equipment_name',
        'equipmentname': 'equipment_name',
        'name': 'equipment_name',
        'equipment': 'equipment_name',
        'type': 'type',
        'equipment_type': 'type',
        'flowrate': 'flowrate',
        'flow_rate': 'flowrate',
        'flow': 'flowrate',
        'pressure': 'pressure',
        'temp': 'temperature',
        'temperature': 'temperature',
    }
    
    return column_mapping.get(normalized, normalized)


def analyze_equipment_csv_from_uploaded_file(uploaded_file: UploadedFile) -> Dict[str, Union[int, float, Dict[str, int], List[Dict[str, Union[str, float]]]]]:
    """
    Analyze CSV from Django UploadedFile object.
    
    Args:
        uploaded_file: Django UploadedFile object
        
    Returns:
        Dictionary containing:
        - total_count: int - number of rows
        - avg_flowrate: float or None - average flowrate
        - avg_pressure: float or None - average pressure  
        - avg_temperature: float or None - average temperature
        - type_distribution: dict - mapping of equipment types to counts
        - preview_rows: list - first 100 rows as dictionaries
        
    Raises:
        CSVParsingError: If CSV is malformed or missing required columns
    """
    try:
        # Reset file pointer to beginning
        uploaded_file.seek(0)
        
        # Read the uploaded file using pandas
        df = pd.read_csv(uploaded_file)
        
        # Check if DataFrame is empty
        if df.empty:
            raise CSVParsingError("CSV file is empty")
        
        # Normalize column names - use .str.strip() and .str.lower()
        df.columns = df.columns.str.strip().str.lower()
        df.columns = [normalize_column_name(str(col)) for col in df.columns]
        
        # Check for required columns (after normalization)
        # Original column names should be: "Equipment Name", "Type", "Flowrate", "Pressure", "Temperature"
        required_columns = ['equipment_name', 'type', 'flowrate', 'pressure', 'temperature']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            # Map back to original expected names for error message
            original_names = {
                'equipment_name': 'Equipment Name',
                'type': 'Type',
                'flowrate': 'Flowrate',
                'pressure': 'Pressure',
                'temperature': 'Temperature'
            }
            missing_original = [original_names.get(col, col) for col in missing_columns]
            raise CSVParsingError(f"Missing required columns: {', '.join(missing_original)}")
        
        # Clean data - remove rows where all required fields are empty
        df_clean = df.dropna(subset=required_columns, how='all')
        
        # Check if we have any valid data after cleaning
        if df_clean.empty:
            raise CSVParsingError("No valid data found after cleaning")
        
        # Convert numeric columns to numeric, coercing errors to NaN
        numeric_columns = ['flowrate', 'pressure', 'temperature']
        for col in numeric_columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Calculate total count (excluding rows with all NaN values)
        total_count = len(df_clean.dropna(subset=required_columns, how='all'))
        
        # Calculate averages, ignoring NaN values
        avg_flowrate = df_clean['flowrate'].mean() if not df_clean['flowrate'].isna().all() else None
        avg_pressure = df_clean['pressure'].mean() if not df_clean['pressure'].isna().all() else None
        avg_temperature = df_clean['temperature'].mean() if not df_clean['temperature'].isna().all() else None
        
        # Calculate type distribution - ensure type column is string
        df_clean['type'] = df_clean['type'].astype(str).str.strip()
        type_counts = df_clean['type'].value_counts()
        type_distribution = type_counts.to_dict()
        
        # Prepare preview rows (limit to first 100)
        preview_df = df_clean.head(100).copy()
        
        # Convert NaN to None for JSON serialization
        preview_df = preview_df.where(pd.notnull(preview_df), None)
        
        # Convert to list of dictionaries
        preview_rows = preview_df.to_dict(orient='records')
        
        # Round averages to 2 decimal places for cleaner output
        if avg_flowrate is not None:
            avg_flowrate = round(avg_flowrate, 2)
        if avg_pressure is not None:
            avg_pressure = round(avg_pressure, 2)
        if avg_temperature is not None:
            avg_temperature = round(avg_temperature, 2)
        
        return {
            'total_count': int(total_count),
            'avg_flowrate': float(avg_flowrate) if avg_flowrate is not None else None,
            'avg_pressure': float(avg_pressure) if avg_pressure is not None else None,
            'avg_temperature': float(avg_temperature) if avg_temperature is not None else None,
            'type_distribution': type_distribution,
            'preview_rows': preview_rows
        }
        
    except pd.errors.EmptyDataError:
        raise CSVParsingError("CSV file is empty or malformed")
    except pd.errors.ParserError as e:
        raise CSVParsingError(f"CSV parsing error: {str(e)}")
    except CSVParsingError:
        raise
    except Exception as e:
        raise CSVParsingError(f"Unexpected error: {str(e)}")
