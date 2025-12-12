
import requests
import sys

try:
    response = requests.get("http://127.0.0.1:8000/api/db-health", timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    if response.status_code == 200:
        print("âœ… API check successful!")
    else:
        print("âŒ API check failed!")
        sys.exit(1)
except Exception as e:
    print("âŒ API check failed with exception!")
    print(e)
    sys.exit(1)
