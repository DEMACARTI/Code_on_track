from app.models.vendor import Vendor

def test_vendor_property():
    v = Vendor(name="Test Vendor", metadata_={"vendor_code": "V123", "notes": "Test Note"})
    print(f"Vendor Name: {v.name}")
    print(f"Vendor Code (Property): {v.vendor_code}")
    print(f"Notes (Property): {v.notes}")
    
    assert v.vendor_code == "V123"
    assert v.notes == "Test Note"
    print("Verification Successful")

if __name__ == "__main__":
    test_vendor_property()
