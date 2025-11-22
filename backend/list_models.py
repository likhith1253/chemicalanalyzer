import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GOOGLE_GEMINI_API_KEY')

if not api_key:
    print("No API key found!")
    exit(1)

genai.configure(api_key=api_key)

print(f"Testing API key: {api_key[:15]}...")
print("\nListing available models:")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  ✅ {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
    print("\nTrying direct model access:")
    
    for model_name in ['models/gemini-1.5-flash', 'models/gemini-pro']:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hi")
            print(f"  ✅ {model_name} WORKS! Response: {response.text[:50]}")
            break
        except Exception as e:
            print(f"  ❌ {model_name}: {str(e)[:100]}")
