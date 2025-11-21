import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

print(f"Checking environment in: {BASE_DIR}")
env_path = BASE_DIR / '.env'
print(f"Looking for .env at: {env_path}")

if env_path.exists():
    print(".env file found.")
    load_dotenv(env_path)
else:
    print(".env file NOT found.")

key = os.getenv('GOOGLE_GEMINI_API_KEY')
if key:
    print("GOOGLE_GEMINI_API_KEY is set.")
    print(f"Key length: {len(key)}")
    print(f"Key starts with: {key[:4]}...")
else:
    print("GOOGLE_GEMINI_API_KEY is NOT set.")

# Check for other common names
for name in ['GEMINI_API_KEY', 'GOOGLE_API_KEY', 'API_KEY']:
    val = os.getenv(name)
    if val:
        print(f"Found alternative key variable: {name}")
