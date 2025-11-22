import requests

url = "https://chemicalanalyzer.onrender.com/api/auth/register/"
data = {
    "username": "quicktest",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!"
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
