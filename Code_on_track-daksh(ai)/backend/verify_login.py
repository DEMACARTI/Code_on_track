import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_login():
    print("Testing Login...")
    url = f"{BASE_URL}/auth/login"
    payload = {"username": "admin", "password": "admin"}
    headers = {"Content-Type": "application/json"}
    
    try:
        r = requests.post(url, json=payload, headers=headers)
        print(f"URL: {url}")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code == 200:
            print("Login SUCCESS!")
            return True
        else:
            print("Login FAILED!")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_login()
