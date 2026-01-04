"""
Test script for CLIP-based shape detection
Run this to verify the model works before testing with camera
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.shape_predict import get_shape_from_image
from PIL import Image, ImageDraw

def create_test_shapes():
    """Create simple test shapes for verification"""
    shapes = {}
    
    # Circle
    img = Image.new('RGB', (200, 200), 'white')
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 150, 150], fill='blue', outline='black', width=3)
    shapes['circle'] = img
    
    # Square
    img = Image.new('RGB', (200, 200), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 150, 150], fill='red', outline='black', width=3)
    shapes['square'] = img
    
    # Triangle
    img = Image.new('RGB', (200, 200), 'white')
    draw = ImageDraw.Draw(img)
    draw.polygon([(100, 40), (40, 160), (160, 160)], fill='green', outline='black', width=3)
    shapes['triangle'] = img
    
    # Rectangle
    img = Image.new('RGB', (300, 200), 'white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 60, 250, 140], fill='purple', outline='black', width=3)
    shapes['rectangle'] = img
    
    # Pentagon (5 sides)
    img = Image.new('RGB', (200, 200), 'white')
    draw = ImageDraw.Draw(img)
    draw.polygon([
        (100, 40), (160, 80), (140, 150), (60, 150), (40, 80)
    ], fill='orange', outline='black', width=3)
    shapes['pentagon'] = img
    
    # Hexagon (6 sides)
    img = Image.new('RGB', (200, 200), 'white')
    draw = ImageDraw.Draw(img)
    draw.polygon([
        (100, 30), (150, 60), (150, 120), (100, 150), (50, 120), (50, 60)
    ], fill='yellow', outline='black', width=3)
    shapes['hexagon'] = img
    
    return shapes

def test_shape_detection():
    """Test CLIP detection on generated shapes"""
    print("🔄 Creating test shapes...")
    test_shapes = create_test_shapes()
    
    print("\n🧪 Testing CLIP Shape Detection\n" + "="*50)
    
    results = []
    for expected_shape, img in test_shapes.items():
        # Save to temp file for testing
        temp_path = f"test_{expected_shape}.png"
        img.save(temp_path)
        
        print(f"\n📸 Testing {expected_shape.upper()}...")
        
        # Test detection
        with open(temp_path, 'rb') as f:
            detected = get_shape_from_image(f)
            
        is_correct = detected.lower() == expected_shape.lower()
        status = "✅" if is_correct else "❌"
        
        print(f"  Expected: {expected_shape}")
        print(f"  Detected: {detected}")
        print(f"  Status: {status}")
        
        results.append({
            'expected': expected_shape,
            'detected': detected,
            'correct': is_correct
        })
    
    # Summary
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    correct = sum(1 for r in results if r['correct'])
    total = len(results)
    accuracy = (correct / total) * 100
    
    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 80:
        print("\n✅ CLIP model is working well!")
    elif accuracy >= 50:
        print("\n⚠️  Model works but may need adjustment")
    else:
        print("\n❌ Model needs improvement")
    
    return results

if __name__ == "__main__":
    print("🚀 Starting CLIP Shape Detection Test\n")
    print("📦 Loading CLIP model (this may take a moment on first run)...")
    
    try:
        results = test_shape_detection()
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
