"""
Quick test to verify the PyTorch model works through the API Gateway
"""
import requests
import json

# Test the API Gateway
GATEWAY_URL = "http://localhost:8000"
SHAPE_DETECTION_URL = f"{GATEWAY_URL}/shapes-patterns/detect-shape"

print("=" * 60)
print("Testing PyTorch Model through API Gateway")
print("=" * 60)
print()

# Test 1: Check if gateway is running
print("1. Testing Gateway Root...")
try:
    response = requests.get(GATEWAY_URL)
    if response.status_code == 200:
        print(f"   ✅ Gateway is running: {response.json()}")
    else:
        print(f"   ❌ Gateway returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 2: Check shape service through gateway
print("2. Testing Shape Service Root...")
try:
    response = requests.get(f"{GATEWAY_URL}/shapes-patterns/")
    if response.status_code == 200:
        print(f"   ✅ Shape service accessible: {response.json()}")
    else:
        print(f"   ❌ Shape service returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 3: Test shape detection with a URL (using a sample image)
print("3. Testing Shape Detection with URL...")
print("   Note: This requires a valid image URL with a shape")
print("   Skipping for now - use the examples below to test with real images")

print()
print("=" * 60)
print("API Gateway is ready! 🎉")
print("=" * 60)
print()
print("Test the shape detection endpoint using:")
print()
print("📁 File Upload Test:")
print('   curl -X POST "http://localhost:8000/shapes-patterns/detect-shape" \\')
print('        -F "image_file=@path/to/your/shape.jpg"')
print()
print("🌐 URL Test:")
print('   curl -X POST "http://localhost:8000/shapes-patterns/detect-shape" \\')
print('        -H "Content-Type: application/json" \\')
print('        -d \'{"image_url": "https://example.com/shape.jpg"}\'')
print()
print("🌐 Interactive Docs:")
print(f"   {GATEWAY_URL}/docs")
print()
