"""
Test script for VGG Model API Integration
Tests all classification endpoints
"""

import requests
import base64
from pathlib import Path
import json

# Configuration
BACKEND_URL = "http://localhost:8000"

def test_health_check():
    """Test if backend is running"""
    print("\n" + "="*70)
    print("1. Testing Health Check")
    print("="*70)
    
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        print(f"✅ Backend is running: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Backend not reachable: {e}")
        return False

def test_model_status():
    """Test model status endpoint"""
    print("\n" + "="*70)
    print("2. Testing Model Status")
    print("="*70)
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/model-status")
        data = response.json()
        
        print(f"Model Loaded: {data['model_loaded']}")
        print(f"Model Type: {data.get('model_type', 'N/A')}")
        print(f"Classes: {data.get('classes', [])}")
        print(f"Status: {data['status']}")
        print(f"Message: {data['message']}")
        
        if data['model_loaded']:
            print("✅ Model is ready for predictions")
            return True
        else:
            print("⚠️  Model not loaded. Train model first:")
            print("   cd railway-vgg-classification")
            print("   python train_vgg_classification.py")
            return False
            
    except Exception as e:
        print(f"❌ Error checking model status: {e}")
        return False

def test_classification_with_file(image_path: str):
    """Test classification with file upload"""
    print("\n" + "="*70)
    print("3. Testing Classification (File Upload)")
    print("="*70)
    
    if not Path(image_path).exists():
        print(f"⚠️  Test image not found: {image_path}")
        print("Skipping file upload test...")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{BACKEND_URL}/api/classify-defect",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Classification successful!")
            print(f"\nPredicted Class: {data['predicted_class']}")
            print(f"Confidence: {data['confidence']:.2%}")
            print(f"Remark: {data['remark']}")
            print(f"\nAll Probabilities:")
            for class_name, prob in data['all_probabilities'].items():
                bar = "█" * int(prob * 50)
                print(f"  {class_name:10s}: {prob:.2%} {bar}")
            return True
        else:
            print(f"❌ Classification failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during classification: {e}")
        return False

def test_classification_with_base64(image_path: str):
    """Test classification with base64 encoded image"""
    print("\n" + "="*70)
    print("4. Testing Classification (Base64)")
    print("="*70)
    
    if not Path(image_path).exists():
        print(f"⚠️  Test image not found: {image_path}")
        print("Skipping base64 test...")
        return False
    
    try:
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Send request
        response = requests.post(
            f"{BACKEND_URL}/api/classify-defect-base64",
            json={'image_base64': image_base64},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Base64 classification successful!")
            print(f"Predicted Class: {data['predicted_class']}")
            print(f"Confidence: {data['confidence']:.2%}")
            return True
        else:
            print(f"❌ Classification failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during base64 classification: {e}")
        return False

def create_test_image():
    """Create a simple test image if none exists"""
    print("\n" + "="*70)
    print("Creating Test Image")
    print("="*70)
    
    try:
        from PIL import Image, ImageDraw
        import random
        
        # Create synthetic test image
        img = Image.new('RGB', (224, 224), color=(200, 200, 200))
        draw = ImageDraw.Draw(img)
        
        # Add some random shapes
        for _ in range(10):
            x, y = random.randint(0, 200), random.randint(0, 200)
            draw.ellipse([x, y, x+20, y+20], fill=(random.randint(100, 200),
                                                    random.randint(50, 150),
                                                    random.randint(50, 150)))
        
        test_path = Path('test_component.jpg')
        img.save(test_path)
        print(f"✅ Created test image: {test_path}")
        return str(test_path)
        
    except Exception as e:
        print(f"❌ Could not create test image: {e}")
        return None

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚂 VGG Model API Integration Test Suite")
    print("="*70)
    
    results = {}
    
    # Test 1: Health check
    results['health'] = test_health_check()
    
    if not results['health']:
        print("\n❌ Backend is not running. Start it with:")
        print("   cd mobile_backend")
        print("   python main.py")
        return
    
    # Test 2: Model status
    results['model_status'] = test_model_status()
    
    if not results['model_status']:
        print("\n⚠️  Cannot proceed without loaded model")
        return
    
    # Find or create test image
    test_image = None
    
    # Try to find existing images in dataset
    dataset_paths = [
        Path('railway-vgg-classification/railway_defect_dataset/test/Rust'),
        Path('railway-vgg-classification/railway_defect_dataset/test/Crack'),
        Path('railway-vgg-classification/railway_defect_dataset/test/Damaged'),
    ]
    
    for path in dataset_paths:
        if path.exists():
            images = list(path.glob('*.jpg')) + list(path.glob('*.png'))
            if images:
                test_image = str(images[0])
                print(f"\n📸 Using test image: {test_image}")
                break
    
    if not test_image:
        test_image = create_test_image()
    
    if test_image:
        # Test 3: File upload classification
        results['file_upload'] = test_classification_with_file(test_image)
        
        # Test 4: Base64 classification
        results['base64'] = test_classification_with_base64(test_image)
    else:
        print("\n⚠️  No test image available, skipping classification tests")
        results['file_upload'] = False
        results['base64'] = False
    
    # Print summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():20s}: {status}")
    
    print("\n" + "="*70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Integration is working correctly.")
    elif results['health'] and results['model_status']:
        print("⚠️  Backend is running but some tests failed.")
        print("This may be normal if you don't have test images yet.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    print("="*70)
    
    # Next steps
    print("\n🎯 Next Steps:")
    if not results['model_status']:
        print("   1. Train the VGG model:")
        print("      cd railway-vgg-classification")
        print("      python download_kaggle_datasets.py")
        print("      python train_vgg_classification.py")
        print("   2. Restart backend server")
        print("   3. Run this test again")
    else:
        print("   1. ✅ Backend is ready for mobile app integration")
        print("   2. Update Flutter app backend URL")
        print("   3. Test camera capture and AI classification in app")
        print("   4. Deploy backend to production server")

if __name__ == "__main__":
    main()
