from pathlib import Path
import pandas as pd
import re
import os
import google.generativeai as genai
from django.core.files.uploadedfile import UploadedFile
import json
from typing import Dict, List, Union, Optional

# Lazy load Gemini to avoid key check on import
try:
    genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))
except Exception:
    # Configuration might fail if key is missing, but that's okay at import time
    pass


class CSVParsingError(Exception):
    """Custom exception for CSV parsing errors."""
    pass


class AIGenerationError(Exception):
    """Custom exception for AI generation errors."""
    pass


def normalize_column_name(column_name: str) -> str:
    """
    Normalize column names to a standard format (snake_case).
    Handles common variations of equipment data column names.
    """
    original = str(column_name).strip()
    lower_original = original.lower()
    
    # Direct mapping for exact matches (fast path)
    exact_mapping = {
        'equipment name': 'equipment_name',
        'equipmentname': 'equipment_name',
        'type': 'type',
        'flowrate': 'flowrate',
        'pressure': 'pressure',
        'temperature': 'temperature',
    }
    
    if lower_original in exact_mapping:
        return exact_mapping[lower_original]
    
    # Standardize: lowercase and replace spaces with underscores
    normalized = lower_original.replace(' ', '_')
    # Remove non-alphanumeric characters except underscores
    normalized = re.sub(r'[^a-z0-9_]', '', normalized)
    
    # Map common variations to standard names
    column_mapping = {
        'name': 'equipment_name',
        'equipment': 'equipment_name',
        'equipment_type': 'type',
        'flow_rate': 'flowrate',
        'flow': 'flowrate',
        'temp': 'temperature',
    }
    
    return column_mapping.get(normalized, normalized)


def analyze_equipment_csv_from_uploaded_file(uploaded_file: UploadedFile) -> Dict[str, Union[int, float, Dict[str, int], List[Dict[str, Union[str, float]]]]]:
    """
    Parses an uploaded CSV file, validates it, and calculates summary statistics.
    Returns a dictionary with total count, averages, type distribution, and preview rows.
    """
    try:
        # Reset file pointer to ensure we read from the beginning
        uploaded_file.seek(0)
        
        # Read CSV
        df = pd.read_csv(uploaded_file)
        
        if df.empty:
            raise CSVParsingError("The uploaded CSV file is empty.")
        
        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()
        df.columns = [normalize_column_name(str(col)) for col in df.columns]
        
        # Define and check for required columns
        required_columns = ['equipment_name', 'type', 'flowrate', 'pressure', 'temperature']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            # Map back to readable names for the error message
            readable_names = {
                'equipment_name': 'Equipment Name',
                'type': 'Type',
                'flowrate': 'Flowrate',
                'pressure': 'Pressure',
                'temperature': 'Temperature'
            }
            missing_readable = [readable_names.get(col, col) for col in missing_columns]
            raise CSVParsingError(f"Missing required columns: {', '.join(missing_readable)}")
        
        # Drop rows where ALL required columns are missing (keep rows with partial data if useful, 
        # but for this strict analysis, we might want to be careful. 
        # The original logic dropped if ALL were missing. Let's stick to that but maybe stricter?)
        # Actually, let's drop rows that are completely empty in the required columns.
        df_clean = df.dropna(subset=required_columns, how='all')
        
        if df_clean.empty:
            raise CSVParsingError("No valid data found after cleaning empty rows.")
        
        # Convert numeric columns to numeric types, coercing errors to NaN
        numeric_columns = ['flowrate', 'pressure', 'temperature']
        for col in numeric_columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Calculate statistics
        # We only count rows that have at least some data
        total_count = len(df_clean)
        
        # Calculate averages (ignoring NaNs)
        avg_flowrate = df_clean['flowrate'].mean()
        avg_pressure = df_clean['pressure'].mean()
        avg_temperature = df_clean['temperature'].mean()
        
        # Type distribution
        # Ensure 'type' is string and handle missing values
        df_clean['type'] = df_clean['type'].fillna('Unknown').astype(str).str.strip()
        type_counts = df_clean['type'].value_counts()
        type_distribution = type_counts.to_dict()
        
        # Prepare preview rows (limit to first 100)
        preview_df = df_clean.head(100).copy()
        # Replace NaN with None for JSON serialization
        preview_df = preview_df.where(pd.notnull(preview_df), None)
        preview_rows = preview_df.to_dict(orient='records')
        
        # Helper to safely round values
        def safe_round(val):
            return round(val, 2) if pd.notnull(val) else None

        return {
            'total_count': int(total_count),
            'avg_flowrate': safe_round(avg_flowrate),
            'avg_pressure': safe_round(avg_pressure),
            'avg_temperature': safe_round(avg_temperature),
            'type_distribution': type_distribution,
            'preview_rows': preview_rows
        }
        
    except pd.errors.EmptyDataError:
        raise CSVParsingError("CSV file is empty or malformed.")
    except pd.errors.ParserError as e:
        raise CSVParsingError(f"CSV parsing error: {str(e)}")
    except CSVParsingError:
        raise
    except Exception as e:
        raise CSVParsingError(f"Unexpected error during CSV analysis: {str(e)}")


def generate_ai_insights(dataset_summary: Dict) -> str:
    """
    Generates AI insights using Google's Gemini model based on the provided dataset summary.
    Tries multiple model versions if the preferred one is unavailable.
    """
    try:
        from google.api_core.exceptions import NotFound, InvalidArgument
        from dotenv import load_dotenv
        
        # 1. Validate API Key
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        
        # Fallback: Try loading .env explicitly if key is missing
        if not api_key:
            print("DEBUG: API Key not found in env, attempting to load .env file explicitly...")
            try:
                # Assuming standard Django structure: backend/chemviz_backend/settings.py -> backend/
                # This file is in backend/equipment/services.py -> backend/
                base_dir = Path(__file__).resolve().parent.parent
                env_path = base_dir / '.env'
                if env_path.exists():
                    print(f"DEBUG: Loading .env from {env_path}")
                    load_dotenv(env_path)
                    api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
            except Exception as e:
                print(f"DEBUG: Failed to load .env explicitly: {e}")

        if not api_key:
            # Raise error so frontend shows the error UI instead of typing this as "insights"
            raise AIGenerationError("API Key missing. Please configure GOOGLE_GEMINI_API_KEY in your environment variables.")
        
        # 2. Configure Gemini
        genai.configure(api_key=api_key)
        
        # 3. Prepare the prompt with data statistics
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
            # Limit to top 5 types to avoid cluttering the prompt
            sorted_types = sorted(type_dist.items(), key=lambda x: x[1], reverse=True)[:5]
            type_list = ", ".join([f"{k}: {v}" for k, v in sorted_types])
            stats_parts.append(f"Top Equipment Types: {type_list}")
        
        stats_text = "\n".join(stats_parts)
        
        prompt = f"""
        Analyze these chemical equipment statistics as a senior industrial engineer:
        
        {stats_text}
        
        Please provide 3 key insights or maintenance recommendations.
        Focus on potential anomalies, efficiency, or safety concerns based on standard industrial values.
        Keep the response concise (bullet points, under 50 words per point).
        """
        
        # 4. Generate content using Gemini
        try:
            # Use gemini-2.5-flash (verified working with current API key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            if not response or not response.text:
                raise AIGenerationError("Model returned empty response")
                
            return response.text.strip()
        except Exception as e:
            error_msg = str(e)
            raise AIGenerationError(f"Failed to generate insights: {error_msg}")
            
    except ImportError:
        return "Error: google-generativeai package is not installed."
    except Exception as e:
        # Log the full error for debugging (in a real app, use a logger)
        print(f"AI Generation Error: {str(e)}")
        return f"Unable to generate insights at this time. Error: {str(e)}"

