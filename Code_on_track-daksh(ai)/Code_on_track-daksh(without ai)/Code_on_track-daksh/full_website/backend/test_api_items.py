import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"

def test_items():
    if not os.path.exists("token.txt"):
        print("Error: token.txt not found. Please run test_login_req.py first.")
        return

    with open("token.txt", "r") as f:
        token = f.read().strip()

    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Requesting {BASE_URL}/items ...")
    try:
        response = requests.get(f"{BASE_URL}/items", headers=headers, params={"page": 1, "page_size": 10}, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print("Success! Response status:", response.status_code)
        print("Total items:", data.get("total"))
        items = data.get("items", [])
        print("Items count in page:", len(items))
        if items:
            print("First item sample:", json.dumps(items[0], indent=2))
        else:
            print("No items found in response.")
            
    except requests.exceptions.Timeout:
        print("Error: Request timed out! (Likely recursion loop / server hang)")
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print("Response:", e.response.text)

if __name__ == "__main__":
    test_items()
