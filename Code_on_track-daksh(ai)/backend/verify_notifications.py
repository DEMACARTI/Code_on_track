import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def verify_notifications():
    print("--- Verifying Notifications System ---")
    
    # 1. Test GET /notifications
    try:
        res = requests.get(f"{BASE_URL}/api/notifications/")
        if res.status_code == 200:
            data = res.json()
            notifications = data.get("notifications", [])
            print(f"✅ GET /notifications success. Count: {len(notifications)}")
            if len(notifications) > 0:
                print(f"Sample: {notifications[0]}")
                # Check keys
                req_keys = ["id", "type", "title", "message", "severity", "read", "created_at"]
                if all(k in notifications[0] for k in req_keys):
                    print("✅ Schema Correct")
                else:
                    print(f"❌ Schema missing keys. Found: {notifications[0].keys()}")
            else:
                print("⚠️ No notifications found (Table might be empty if seed failed)")
        else:
            print(f"❌ GET failed: {res.status_code} - {res.text}")
            
    except Exception as e:
        print(f"❌ GET Error: {e}")

    # 2. Test Auto-Generation (Scheduler runs every 60s, but we just started)
    # We can check if 'high_risk' or 'anomaly' types exist in the list
    try:
        res = requests.get(f"{BASE_URL}/api/notifications/")
        if res.status_code == 200:
            notifications = res.json().get("notifications", [])
            types = [n['type'] for n in notifications]
            print(f"Notification Types Found: {set(types)}")
            
            expected = ['high_risk', 'anomaly', 'system'] # system from seed
            found = [t for t in expected if t in types]
            if found:
                print(f"✅ Found Expected Types: {found}")
            else:
                 print("⚠️ Only seed data or empty? Wait for scheduler.")

    except Exception as e:
        print(e)
        
    # 3. Test Mark Read
    if notifications:
        try:
            nid = notifications[0]['id']
            print(f"Marking ID {nid} as read...")
            res = requests.patch(f"{BASE_URL}/api/notifications/read/{nid}")
            if res.status_code == 200:
                print("✅ Mark Read Success")
            else:
                print(f"❌ Mark Read Failed: {res.status_code}")
        except Exception as e:
            print(f"❌ Mark Read Error: {e}")

if __name__ == "__main__":
    verify_notifications()
