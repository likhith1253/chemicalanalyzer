import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Load env
base_dir = Path(__file__).resolve().parent
env_path = base_dir / '.env'
load_dotenv(env_path)

api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
if not api_key:
    print("Error: GOOGLE_GEMINI_API_KEY not found.")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
