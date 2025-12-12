import urllib.request
import json
import sys

def check_api():
    url = "http://localhost:8000/analytics/summary"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                print(f"Error: Status {response.status}")
                sys.exit(1)
            
            data = json.loads(response.read().decode())
            print(f"API_RESPONSE: {json.dumps(data)}")
            
            critical_lots = data.get("lot_quality")
            print(f"CRITICAL_LOTS_FROM_API: {critical_lots}")

    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_api()
