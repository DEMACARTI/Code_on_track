import urllib.request
import json
import sys

def verify_vendors():
    url = "http://localhost:8000/vendors"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                print(f"Error: Status {response.status}")
                sys.exit(1)
            
            data = json.loads(response.read().decode())
            vendors = data.get("vendors", [])
            
            missing_codes = 0
            for v in vendors:
                code = v.get("vendor_code")
                if not code:
                    print(f"FAILED: Vendor {v['name']} (ID: {v['id']}) has no code.")
                    missing_codes += 1
                else:
                    print(f"OK: Vendor {v['name']} (ID: {v['id']}) has code: {code}")
            
            if missing_codes == 0:
                print("\nSUCCESS: All vendors have codes.")
            else:
                print(f"\nFAILURE: {missing_codes} vendors missing codes.")
                sys.exit(1)

    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_vendors()
