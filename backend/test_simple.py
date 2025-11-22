import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
print(f"API Key found: {api_key[:10]}...{api_key[-4:] if api_key else 'NONE'}")

if not api_key:
    print("ERROR: No API key!")
    sys.exit(1)

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say hello")
    print(f"SUCCESS! Response: {response.text}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}")
    print(f"Message: {str(e)}")
