import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def verify_fixes():
    try:
        print("Waiting for server...")
        time.sleep(3)
        
        print("\n--- 1. Testing Weekly Defects ---")
        try:
            res = requests.get(f"{BASE_URL}/api/analytics/weekly_defects", timeout=5)
            if res.status_code == 200:
                data = res.json()
                print(f"Status: {res.status_code}")
                # Check structure
                days = [d['day'] for d in data] if isinstance(data, list) else []
                print(f"Days present: {days}")
                expected_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                if days == expected_days:
                    print("✅ Days are strictly ordered Mon-Sun")
                else:
                    print("❌ Days ordering mismatch")
            else:
                print(f"❌ Failed: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"❌ Request Error: {e}")

        print("\n--- 2. Testing Items Columns ---")
        try:
            res = requests.get(f"{BASE_URL}/api/items/?size=1", timeout=5)
            if res.status_code == 200:
                data = res.json()
                items = data.get('items', [])
                if items:
                    item = items[0]
                    # Check for keys
                    if 'depot' in item and 'manufacture' in item:
                        print(f"✅ 'depot' and 'manufacture' keys present")
                        print(f"Values -> Depot: {item.get('depot')}, Manufacture: {item.get('manufacture')}")
                    else:
                        print(f"❌ Missing keys. Present: {list(item.keys())}")
                else:
                    print("⚠️ No items to check")
            else:
                print(f"❌ Failed: {res.status_code}")
        except Exception as e:
            print(f"❌ Request Error: {e}")

        print("\n--- 3. Testing Analytics Summary ---")
        try:
            res = requests.get(f"{BASE_URL}/api/analytics/summary", timeout=5)
            if res.status_code == 200:
                data = res.json()
                # Check keys
                required = ['critical_lots', 'analyzed_lots', 'vendors', 'total_items']
                if all(k in data for k in required):
                    print("✅ All KPI keys present")
                    print(f"Critical Lots: {data.get('critical_lots')}")
                    print(f"Analyzed Lots: {data.get('analyzed_lots')}")
                else:
                    print(f"❌ Missing KPI keys. Present: {list(data.keys())}")
            else:
                print(f"❌ Failed: {res.status_code}")
        except Exception as e:
            print(f"❌ Request Error: {e}")

    except Exception as e:
        print(f"❌ Verification Logic Error: {e}")

if __name__ == "__main__":
    verify_fixes()
