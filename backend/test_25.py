import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
genai.configure(api_key=api_key)

models_to_test = [
    'gemini-2.5-flash',
    'gemini-2.5-pro',
    'gemini-2.0-flash-exp',
    'gemini-exp-1206',
]

for model_name in models_to_test:
    try:
        print(f"Testing {model_name}...", end=" ")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say OK")
        print(f"✓ WORKS! Response: {response.text[:20]}")
        break  # Found working model
    except Exception as e:
        print(f"✗ {str(e)[:50]}")
