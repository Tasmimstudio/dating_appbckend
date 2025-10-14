import requests
import json

url = "http://127.0.0.1:8000/auth/register"
data = {
    "name": "John Smith",
    "email": "john@example.com",
    "password": "John123!",
    "age": 28,
    "gender": "male",
    "bio": "Software engineer who loves hiking and photography"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code == 200:
        print(f"Success! User created: {response.json()}")
    else:
        print(f"Error: {response.json()}")
except Exception as e:
    print(f"Exception: {e}")
