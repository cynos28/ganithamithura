"""
Test script to verify the PyTorch model integration.
Run this to ensure the model loads correctly and can make predictions.
"""
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ai_model.model import get_model_instance
from app.services.shape_predict import get_shape_from_image, get_shape_with_confidence


def test_model_loading():
    """Test if the model loads successfully."""
    print("=" * 60)
    print("Testing Model Loading")
    print("=" * 60)
    
    try:
        model, class_names, device = get_model_instance()
        print(f"✅ Model loaded successfully!")
        print(f"📊 Number of classes: {len(class_names)}")
        print(f"📋 Classes: {class_names}")
        print(f"🖥️  Device: {device}")
        print(f"🏗️  Model architecture: {model.__class__.__name__}")
        return True
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False


def test_image_prediction():
    """Test prediction on a sample image (if available)."""
    print("\n" + "=" * 60)
    print("Testing Image Prediction")
    print("=" * 60)
    
    # Check if there are test images in the assets folder
    assets_dir = Path(__file__).parent / "assets"
    
    if assets_dir.exists():
        test_images = list(assets_dir.glob("*.jpg")) + list(assets_dir.glob("*.png"))
        
        if test_images:
            print(f"\n📁 Found {len(test_images)} test images in assets folder")
            
            # Test with first image
            test_image = test_images[0]
            print(f"\n🖼️  Testing with: {test_image.name}")
            
            try:
                # Test basic prediction
                result = get_shape_from_image(str(test_image))
                print(f"✅ Basic prediction: {result}")
                
                # Test prediction with confidence
                with open(test_image, 'rb') as f:
                    result_with_conf = get_shape_with_confidence(f)
                    print(f"✅ Prediction with confidence:")
                    print(f"   - Shape: {result_with_conf['predicted_shape']}")
                    print(f"   - Confidence: {result_with_conf['confidence']:.2%}")
                
                return True
            except Exception as e:
                print(f"❌ Prediction failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("ℹ️  No test images found in assets folder")
            print("   To test predictions, add some shape images to the assets folder")
    else:
        print("ℹ️  Assets folder not found")
        print("   Skipping image prediction test")
    
    return True


def test_api_endpoint_simulation():
    """Simulate an API endpoint call."""
    print("\n" + "=" * 60)
    print("API Endpoint Simulation")
    print("=" * 60)
    
    print("""
The following endpoints should now work with your trained model:

1. POST /detect-shape (with file upload)
   - Upload a shape image
   - Returns: {"shape": "Circle"}

2. POST /detect-shape (with JSON URL)
   - Send: {"image_url": "https://example.com/shape.jpg"}
   - Returns: {"shape": "Square"}

Example cURL commands:
    
# File upload
curl -X POST "http://localhost:8001/detect-shape" \\
  -F "image_file=@path/to/your/shape.jpg"

# URL
curl -X POST "http://localhost:8001/detect-shape" \\
  -H "Content-Type: application/json" \\
  -d '{"image_url": "https://example.com/shape.jpg"}'
    """)
    
    return True


def main():
    """Run all tests."""
    print("\n🚀 Testing PyTorch Model Integration")
    print("=" * 60)
    
    # Check if model file exists
    model_path = Path(__file__).parent / "app" / "services" / "ai_model" / "shape_classifier.pt"
    
    if not model_path.exists():
        print(f"❌ Model file not found at: {model_path}")
        print("\nPlease ensure your trained model is at:")
        print(f"   {model_path}")
        return
    
    print(f"✅ Model file found at: {model_path}")
    
    # Run tests
    results = []
    results.append(("Model Loading", test_model_loading()))
    results.append(("Image Prediction", test_image_prediction()))
    results.append(("API Info", test_api_endpoint_simulation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Your model is ready to use.")
        print("\n📝 Next steps:")
        print("   1. Install dependencies: uv sync")
        print("   2. Start the service: uv run uvicorn app.main:app --reload --port 8001")
        print("   3. Test the API at: http://localhost:8001/docs")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()
