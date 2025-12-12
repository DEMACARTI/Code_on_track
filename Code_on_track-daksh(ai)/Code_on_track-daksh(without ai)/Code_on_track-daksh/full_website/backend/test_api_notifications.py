
import requests
import sys
import json

try:
    with open("token.txt", "r") as f:
        token = f.read().strip()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 1. Unread Count
    print("GET /unread_count")
    resp = requests.get("http://localhost:8000/api/notifications/unread_count", headers=headers)
    print(resp.status_code, resp.json())
    
    # 2. List Notifications (All)
    print("\nGET / (All)")
    resp = requests.get("http://localhost:8000/api/notifications?unread=false&limit=5", headers=headers)
    print(resp.status_code)
    data = resp.json()
    print("All Count:", len(data.get("notifications", [])))
    
    # 2b. List Notifications (Unread)
    print("\nGET /?unread=true")
    resp = requests.get("http://localhost:8000/api/notifications?unread=true&limit=5", headers=headers)
    print(resp.status_code)
    data = resp.json()
    print("Unread Count:", data.get("unread_count"))
    notifs = data.get("notifications", [])
    print(f"Got {len(notifs)} notifications")
    if notifs:
        print("Sample:", notifs[0]['title'])
        first_id = notifs[0]['id']
        
        # 3. Mark Read
        print(f"\nPOST /mark_read for ID {first_id}")
        resp = requests.post("http://localhost:8000/api/notifications/mark_read", headers=headers, json={"ids": [first_id]})
        print(resp.status_code, resp.json())
        
        # 4. Dismiss
        print(f"\nPOST /dismiss for ID {first_id}")
        resp = requests.post("http://localhost:8000/api/notifications/dismiss", headers=headers, json={"ids": [first_id]})
        print(resp.status_code, resp.json())

except Exception as e:
    print(f"Error: {e}")
