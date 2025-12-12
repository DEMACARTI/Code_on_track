import requests
import time
import json

BASE_URL = "http://127.0.0.1:5000/api"

def check_backend():
    print("Checking backend health...")
    try:
        r = requests.get(f"http://127.0.0.1:5000/health")
        if r.status_code == 200:
            print("Backend is alive.")
            return True
    except:
        print("Backend not responding.")
    return False

def run_jobs():
    print("\n--- Triggering Jobs ---")
    
    # 1. Quality Job
    # Check if endpoint exists
    try:
        print("Triggering /lot_quality/run_job...")
        r = requests.post(f"{BASE_URL}/lot_quality/run_job")
        print(f"Status: {r.status_code}, Response: {r.text}")
    except Exception as e:
        print(f"Error calling quality job: {e}")

    # 2. Health Job
    try:
        print("Triggering /lot_health/run_job...")
        r = requests.post(f"{BASE_URL}/lot_health/run_job")
        print(f"Status: {r.status_code}, Response: {r.text}")
    except Exception as e:
        print(f"Error calling health job: {e}")

    # 3. Debug Status
    try:
        print("Fetching /debug/status...")
        r = requests.get(f"{BASE_URL}/debug/status")
        print(f"Debug Status: {json.dumps(r.json(), indent=2)}")
    except Exception as e:
        print(f"Error calling debug status: {e}")

if __name__ == "__main__":
    # Wait a bit for server to restart if called immediately after restart command
    time.sleep(5)
    if check_backend():
        run_jobs()
    else:
        print("Exiting verification (backend down).")
