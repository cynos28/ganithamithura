"""
Test the Shape Detection API
Make sure the service is running before executing this script
"""
import requests
from PIL import Image, ImageDraw
import io

# Service URL
BASE_URL = "http://localhost:8002"

def create_test_image(shape_type):
    """Create a simple test image"""
    img = Image.new('RGB', (300, 300), 'white')
    draw = ImageDraw.Draw(img)
    
    if shape_type == "circle":
        draw.ellipse([75, 75, 225, 225], fill='blue', outline='black', width=3)
    elif shape_type == "square":
        draw.rectangle([75, 75, 225, 225], fill='red', outline='black', width=3)
    elif shape_type == "triangle":
        draw.polygon([(150, 50), (50, 250), (250, 250)], fill='green', outline='black', width=3)
    elif shape_type == "rectangle":
        draw.rectangle([50, 100, 250, 200], fill='purple', outline='black', width=3)
    
    return img

def test_detect_shape(shape_type):
    """Test shape detection API"""
    print(f"\n🧪 Testing {shape_type.upper()} detection...")
    
    # Create test image
    img = create_test_image(shape_type)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Send to API
    url = f"{BASE_URL}/detect-shape/"
    files = {'image_file': ('test_shape.png', img_bytes, 'image/png')}
    
    try:
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            detected = result.get('shape', 'Unknown')
            
            is_correct = detected.lower() == shape_type.lower()
            status = "✅" if is_correct else "❌"
            
            print(f"  Expected: {shape_type}")
            print(f"  Detected: {detected}")
            print(f"  Status: {status}")
            
            return is_correct
        else:
            print(f"  ❌ API Error: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("  ❌ Connection Error: Is the service running?")
        print(f"  Start with: uvicorn app.main:app --reload --port 8002")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_health():
    """Test if service is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Service is running")
            print(f"   {response.json()}")
            return True
        else:
            print("❌ Service returned error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to service")
        print(f"   URL: {BASE_URL}")
        print("   Start with: uvicorn app.main:app --reload --port 8002")
        return False

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   Shape Detection API Test                               ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    print(f"🌐 Testing API at: {BASE_URL}")
    
    # Check if service is running
    if not test_health():
        return
    
    print("\n" + "="*60)
    print("Testing Shape Detection")
    print("="*60)
    
    # Test shapes
    test_shapes = ["circle", "square", "triangle", "rectangle"]
    results = []
    
    for shape in test_shapes:
        result = test_detect_shape(shape)
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    correct = sum(results)
    total = len(results)
    accuracy = (correct / total * 100) if total > 0 else 0
    
    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 75:
        print("\n✅ API is working well!")
    else:
        print("\n⚠️  API needs attention")
    
    print("""
    \n💡 Next Steps:
    • Test with Flutter camera app
    • Point camera at real objects
    • Verify 3D shape detection (cube, sphere, etc.)
    """)

if __name__ == "__main__":
    main()
