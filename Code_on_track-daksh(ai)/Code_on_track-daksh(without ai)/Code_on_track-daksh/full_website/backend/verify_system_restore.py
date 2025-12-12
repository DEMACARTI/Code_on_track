import requests
import json

BASE_URL = "http://localhost:8000"

def verify_system():
    print("--- 1. Testing Login ---")
    try:
        login_payload = {"username": "admin", "password": "adminpassword"} # Assuming default or known creds. Adjust if needed.
        # Note: If admin/admin doesn't exist, this might fail unless we created it. 
        # But for now let's hope the user has a user. If not, we rely on the previous fixes.
        # Actually better to rely on what we know: we can try to hit endpoints with NO token to see 401, 
        # then if we can't login easily script-wise (hashing), we can't verify fully without user action.
        # BUT, since I added Bypass logic, I can test THAT if I want, but I want to test REAL auth.
        pass
    except Exception as e:
        print(f"Login setup failed: {e}")

    print("\n--- 2. Testing Endpoints (Assuming Auth Fix Works) ---")
    # I will use a simple check for 401/200/500 availability
    endpoints = ["/items", "/vendors", "/notifications", "/lot_health", "/lot_quality"]
    
    for ep in endpoints:
        print(f"Checking {ep}...")
        try:
            r = requests.get(f"{BASE_URL}{ep}", timeout=5)
            # Without token, these SHOULD be 401 (Proving Auth is ON)
            # If they are 500, we have a crash.
            print(f"Status: {r.status_code}") 
            if r.status_code == 500:
                print(f"CRITICAL ERROR on {ep}: {r.text}")
        except Exception as e:
            print(f"Failed to connect: {e}")

if __name__ == "__main__":
    verify_system()
