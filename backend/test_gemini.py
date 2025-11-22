import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env
load_dotenv()

api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
if not api_key:
    print("ERROR: GOOGLE_GEMINI_API_KEY not found in .env")
    exit(1)

# Configure Gemini
genai.configure(api_key=api_key)

print("Testing which Gemini models work with your API key...\n")

models_to_test = [
    'gemini-2.0-flash-exp',
    'gemini-1.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-pro',
    'gemini-1.5-pro-latest',
    'gemini-pro',
]

working_models = []

for model_name in models_to_test:
    try:
        print(f"Testing {model_name}...", end=" ")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'OK'")
        if response and response.text:
            print("✅ WORKS")
            working_models.append(model_name)
        else:
            print("❌ No response")
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")

print(f"\n{'='*60}")
print(f"Working models: {working_models}")
print(f"{'='*60}")

if working_models:
    print(f"\nRecommended model to use: {working_models[0]}")
else:
    print("\nNO MODELS WORK! Check your API key.")
