import requests
import base64
import json
from pathlib import Path

# Read the image file
image_path = "/tmp/rusted_railway.jpg"

# Check if render is up
print("🔍 Checking Render API status...")
health_response = requests.get("https://railchinh-mobile-backend.onrender.com/")
print(f"Status: {health_response.json()}")

# Check model status
print("\n🤖 Checking model status...")
model_response = requests.get("https://railchinh-mobile-backend.onrender.com/api/model-status")
print(f"Model Status: {json.dumps(model_response.json(), indent=2)}")

# If model is loaded, test classification
if model_response.json().get("model_loaded"):
    print("\n📸 Testing rust classification...")
    
    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    # Send to API
    classify_response = requests.post(
        "https://railchinh-mobile-backend.onrender.com/api/classify-defect-base64",
        json={"image_data": image_data}
    )
    
    result = classify_response.json()
    print(f"\n✅ Classification Result:")
    print(f"   Predicted Class: {result['predicted_class']}")
    print(f"   Confidence: {result['confidence']:.2%}")
    print(f"   Remark: {result['remark']}")
    print(f"\n📊 All Probabilities:")
    for class_name, prob in sorted(result['all_probabilities'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {class_name}: {prob:.2%}")
else:
    print("\n⚠️  Model not loaded yet. Wait for deployment to complete.")

