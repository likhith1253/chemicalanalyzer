import pandas as pd
import re
import os
from typing import Dict, List, Optional, Union
from django.core.files.uploadedfile import UploadedFile


class CSVParsingError(Exception):
    # CSV parsing error
    pass


class AIGenerationError(Exception):
    # AI generation error
    pass


def normalize_column_name(column_name: str) -> str:
    # Normalize column names
    original = str(column_name).strip()
    
    # Direct mapping
    exact_mapping = {
        'equipment name': 'equipment_name',
        'equipmentname': 'equipment_name',
        'type': 'type',
        'flowrate': 'flowrate',
        'pressure': 'pressure',
        'temperature': 'temperature',
    }
    
    # Check exact match
    lower_original = original.lower().strip()
    if lower_original in exact_mapping:
        return exact_mapping[lower_original]
    
    # Convert to lowercase, replace spaces
    normalized = lower_original.replace(' ', '_')
    normalized = re.sub(r'[^a-z0-9_]', '', normalized)
    
    # Map variations
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
    # Analyze CSV file
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Read CSV
        df = pd.read_csv(uploaded_file)
        
        # Check if empty
        if df.empty:
            raise CSVParsingError("CSV file is empty")
        
        # Normalize columns
        df.columns = df.columns.str.strip().str.lower()
        df.columns = [normalize_column_name(str(col)) for col in df.columns]
        
        # Check required columns
        required_columns = ['equipment_name', 'type', 'flowrate', 'pressure', 'temperature']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            # Map back for error message
            original_names = {
                'equipment_name': 'Equipment Name',
                'type': 'Type',
                'flowrate': 'Flowrate',
                'pressure': 'Pressure',
                'temperature': 'Temperature'
            }
            missing_original = [original_names.get(col, col) for col in missing_columns]
            raise CSVParsingError(f"Missing required columns: {', '.join(missing_original)}")
        
        # Clean data
        df_clean = df.dropna(subset=required_columns, how='all')
        
        # Check if any valid data
        if df_clean.empty:
            raise CSVParsingError("No valid data found after cleaning")
        
        # Convert numeric columns
        numeric_columns = ['flowrate', 'pressure', 'temperature']
        for col in numeric_columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Calculate stats
        total_count = len(df_clean.dropna(subset=required_columns, how='all'))
        
        # Calculate averages
        avg_flowrate = df_clean['flowrate'].mean() if not df_clean['flowrate'].isna().all() else None
        avg_pressure = df_clean['pressure'].mean() if not df_clean['pressure'].isna().all() else None
        avg_temperature = df_clean['temperature'].mean() if not df_clean['temperature'].isna().all() else None
        
        # Type distribution
        df_clean['type'] = df_clean['type'].astype(str).str.strip()
        type_counts = df_clean['type'].value_counts()
        type_distribution = type_counts.to_dict()
        
        # Preview rows (limit 100)
        preview_df = df_clean.head(100).copy()
        preview_df = preview_df.where(pd.notnull(preview_df), None)
        preview_rows = preview_df.to_dict(orient='records')
        
        # Round averages
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


def generate_ai_insights(dataset_summary: Dict) -> str:
    # Generate AI insights using Gemini
    try:
        import google.generativeai as genai
        from google.api_core.exceptions import NotFound, InvalidArgument
        
        # Check API key
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        if not api_key:
            raise AIGenerationError("API Key not configured. Please set GOOGLE_GEMINI_API_KEY environment variable.")
        
        # Configure API
        genai.configure(api_key=api_key)
        
        # Prepare stats
        stats_parts = []
        stats_parts.append(f"Total Equipment Count: {dataset_summary.get('total_count', 0)}")
        
        if dataset_summary.get('avg_flowrate') is not None:
            stats_parts.append(f"Average Flowrate: {dataset_summary.get('avg_flowrate')} L/min")
        if dataset_summary.get('avg_pressure') is not None:
            stats_parts.append(f"Average Pressure: {dataset_summary.get('avg_pressure')} bar")
        if dataset_summary.get('avg_temperature') is not None:
            stats_parts.append(f"Average Temperature: {dataset_summary.get('avg_temperature')} °C")
        
        type_dist = dataset_summary.get('type_distribution', {})
        if type_dist:
            type_list = ", ".join([f"{k}: {v}" for k, v in type_dist.items()])
            stats_parts.append(f"Equipment Types: {type_list}")
        
        stats_text = "\n".join(stats_parts)
        
        # Build prompt
        prompt = f"""Analyze these chemical equipment statistics:
{stats_text}

Identify 3 potential anomalies or maintenance recommendations based on standard industrial engineering principles. Keep it concise (under 50 words per point). Format as a numbered list."""
        
        # Try multiple models
        models_to_try = ['gemini-2.5-pro', 'gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
        last_error = None
        response = None
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                break  # Success
            except (NotFound, InvalidArgument) as model_error:
                last_error = model_error
                print(f"WARNING: Model '{model_name}' not available, trying next...")
                continue
        
        if not response or not response.text:
            # All models failed
            print("ERROR: All tried models failed. Available models:")
            try:
                for model_info in genai.list_models():
                    print(f"  - {model_info.name}")
            except Exception as list_error:
                print(f"  Could not list models: {list_error}")
            raise AIGenerationError(f"No available models found. Tried: {', '.join(models_to_try)}. Last error: {str(last_error)}")
        
        # Return response
        if response and response.text:
            return response.text.strip()
        else:
            raise AIGenerationError("Empty response from AI model")
            
    except ImportError:
        raise AIGenerationError("google-generativeai package not installed. Please install it using: pip install google-generativeai")
    except (NotFound, InvalidArgument) as e:
        raise AIGenerationError(f"Model error: {str(e)}")
    except AIGenerationError:
        raise
    except Exception as e:
        raise AIGenerationError(f"Failed to generate AI insights: {str(e)}")
