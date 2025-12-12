
import requests
import sys

try:
    response = requests.post(
        "http://localhost:8000/auth/login",
        json={"username": "admin", "password": "admin"},
        timeout=5
    )
    token = response.json().get("access_token")
    if token:
        with open("token.txt", "w") as f:
            f.write(token)
        print("Token saved to token.txt")
    else:
        print("NO_TOKEN")
except Exception as e:
    print(f"Error: {e}")
