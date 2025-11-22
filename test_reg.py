import requests
import json
import random
import string

# Generate random user
username = "test_" + ''.join(random.choices(string.ascii_lowercase, k=5))
password = "TestPass123!"
email = f"{username}@example.com"

url = "https://chemicalanalyzer.onrender.com/api/auth/register/"
data = {
    "username": username,
    "password": password,
    "password_confirm": password,
    "email": email
}

print(f"Attempting to register user: {username}")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
