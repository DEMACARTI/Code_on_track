import requests
import json
import time
import sys

# Add the project root to the Python path
sys.path.append('.')

# Base URL of the API
BASE_URL = "http://localhost:8000/api"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*50}")
    print(f" {title}".ljust(48, ' ') + " ")
    print(f"{'='*50}")

def test_health_check():
    """Test the health check endpoint"""
    print("\nTesting health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error during health check: {str(e)}")
        return False

def test_create_item():
    """Test creating a new item"""
    print("\nTesting item creation...")
    data = {
        "component_type": "ERC",
        "lot_number": "LOT12345",
        "vendor_id": "VENDOR001",
        "warranty_years": 5,
        "manufacture_date": "2025-11-22",
        "quantity": 1
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/items/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:  # 201 Created
            result = response.json()
            print("✅ Item created successfully!")
            print("Response:", json.dumps(result, indent=2))
            return result["items"][0]["uid"]
        else:
            print(f"❌ Failed to create item: {response.status_code}")
            print("Response:", response.text)
            return None
    except Exception as e:
        print(f"❌ Error during item creation: {str(e)}")
        return None

def test_get_item(uid):
    """Test retrieving an item by UID"""
    print(f"\nTesting retrieval of item {uid}...")
    try:
        response = requests.get(f"{BASE_URL}/items/{uid}")
        
        if response.status_code == 200:
            print("✅ Item retrieved successfully!")
            print("Item details:", json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Failed to retrieve item: {response.status_code}")
            print("Response:", response.text)
            return False
    except Exception as e:
        print(f"❌ Error retrieving item: {str(e)}")
        return False

def test_create_multiple_items():
    """Test creating multiple items at once"""
    print("\nTesting bulk item creation...")
    data = {
        "component_type": "SLP",
        "lot_number": "LOT54321",
        "vendor_id": "VENDOR002",
        "warranty_years": 10,
        "manufacture_date": "2025-11-22",
        "quantity": 3
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/items/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:  # 201 Created
            result = response.json()
            print(f"✅ Successfully created {result['total_created']} items!")
            print("Created items:", json.dumps(result["items"], indent=2))
            return [item["uid"] for item in result["items"]]
        else:
            print(f"❌ Failed to create items: {response.status_code}")
            print("Response:", response.text)
            return []
    except Exception as e:
        print(f"❌ Error during bulk item creation: {str(e)}")
        return []

def run_tests():
    """Run all tests"""
    print_section("🚀 Starting API Tests")
    
    # Wait for the server to start
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run tests
    success = True
    
    # Test 1: Health check
    if not test_health_check():
        success = False
    
    # Test 2: Create a single item
    uid = test_create_item()
    if uid:
        # Test 3: Retrieve the created item
        if not test_get_item(uid):
            success = False
    else:
        success = False
    
    # Test 4: Create multiple items
    uids = test_create_multiple_items()
    if uids:
        # Test 5: Retrieve each created item
        for uid in uids:
            if not test_get_item(uid):
                success = False
    else:
        success = False
    
    # Print final result
    print_section("✨ Test Results")
    if success:
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed. Please check the logs above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(run_tests())
