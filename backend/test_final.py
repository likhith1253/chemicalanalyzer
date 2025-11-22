import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
genai.configure(api_key=api_key)

# Test WITHOUT models/ prefix
model_name = 'gemini-1.5-flash'
print(f"Testing {model_name}...")

try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say OK")
    print(f"SUCCESS! Response: {response.text}")
except Exception as e:
    print(f"FAILED: {e}")
