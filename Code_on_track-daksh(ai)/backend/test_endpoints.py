import sys
import os
from flask import json

# Ensure backend is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app import create_app

def test_endpoints():
    print("Initializing Flask app...")
    app = create_app()
    client = app.test_client()
    
    print("\n--- Testing /api/db-health/ ---")
    res = client.get('/api/db-health/', follow_redirects=True)
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.data.decode('utf-8')}")
    
    if res.status_code == 200:
        data = json.loads(res.data)
        if data.get('status') == 'ok' and data.get('database') == 'connected':
             print("SUCCESS: Database health check passed.")
        else:
             print("FAILURE: Database health check returned unexpected status.")
    else:
        print("FAILURE: Health check endpoint returned error.")

    print("\n--- Testing /api/items/ ---")
    try:
        res = client.get('/api/items/')
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.data.decode('utf-8')[:200]}...")
    except Exception as e:
         print(f"Error testing items: {e}")

    print("\n--- Testing /api/analytics/summary ---")
    try:
        res = client.get('/api/analytics/summary')
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.data.decode('utf-8')[:200]}...")
    except Exception as e:
         print(f"Error testing summary: {e}")

    print("\n--- Testing /api/lot-quality/ ---")
    try:
        res = client.get('/api/lot-quality/')
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.data.decode('utf-8')[:200]}...")
    except Exception as e:
         print(f"Error testing lot-quality: {e}")

if __name__ == "__main__":
    test_endpoints()
