import urllib.request
import json
import sys

def test_api():
    url = "http://localhost:8000/lot_health/?risk_level=CRITICAL"
    print(f"Testing URL: {url}")
    try:
        with urllib.request.urlopen(url) as response:
            print(f"Status: {response.status}")
            data = response.read()
            print(f"Response Body (truncated): {data[:200]}")
            try:
                json_data = json.loads(data)
                print("JSON Decode Success")
                print(f"Item count: {len(json_data)}")
            except json.JSONDecodeError as e:
                 print(f"JSON Decode Error: {e}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(e.read())
    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    test_api()
