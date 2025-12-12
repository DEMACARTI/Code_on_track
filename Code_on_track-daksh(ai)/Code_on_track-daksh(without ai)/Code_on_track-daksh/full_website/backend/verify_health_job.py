import urllib.request
import json

try:
    req = urllib.request.Request("http://localhost:8000/lot_health/run_job", method="POST")
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            data = json.loads(response.read().decode())
            print(f"SUCCESS: {json.dumps(data)}")
        else:
            print(f"FAILED: {response.status}")
except Exception as e:
    print(f"ERROR: {e}")
