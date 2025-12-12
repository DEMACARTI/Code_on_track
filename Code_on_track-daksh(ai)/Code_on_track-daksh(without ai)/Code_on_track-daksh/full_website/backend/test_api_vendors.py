
import requests
import sys

try:
    with open("token.txt", "r") as f:
        token = f.read().strip()
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        "http://localhost:8000/vendors",
        headers=headers,
        timeout=5
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}") # First 500 chars
    
    # Parse json and check components
    data = response.json()
    for v in data[:3]:
        print(f"Vendor: {v['name']}, Components: {v.get('components_supplied')}")

except Exception as e:
    print(f"Error: {e}")
