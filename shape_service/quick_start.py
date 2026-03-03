"""
Quick Start Script for CLIP Shape Detection
Run this to set up and test the service
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and display output"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        
        print(f"✅ {description} - Complete")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   CLIP Shape Detection - Quick Start                     ║
    ║   Zero-shot shape recognition for 11 shapes              ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    print(f"🐍 Python Version: {sys.version}")
    
    # Step 1: Check if in correct directory
    current_dir = Path.cwd()
    if not (current_dir / "app" / "services" / "shape_predict.py").exists():
        print("❌ Error: Please run this script from the shape_service directory")
        print(f"   Current directory: {current_dir}")
        print("   Expected: ganithamithura/shape_service/")
        return
    
    print(f"📂 Working Directory: {current_dir}")
    
    # Step 2: Install/Update dependencies
    print("\n" + "="*60)
    choice = input("Install/Update dependencies? (y/n): ")
    if choice.lower() == 'y':
        run_command(
            "pip install -e .",
            "Installing dependencies"
        )
    
    # Step 3: Test CLIP model
    print("\n" + "="*60)
    choice = input("Run CLIP detection test? (y/n): ")
    if choice.lower() == 'y':
        print("\n⏳ Loading CLIP model (this may take a moment on first run)...")
        print("   Model will be cached for future use (~600MB)")
        run_command(
            "python test_clip_detection.py",
            "Testing CLIP shape detection"
        )
    
    # Step 4: Start service
    print("\n" + "="*60)
    choice = input("Start the shape service? (y/n): ")
    if choice.lower() == 'y':
        print("\n🚀 Starting Shape Service on http://localhost:8002")
        print("   Press Ctrl+C to stop")
        print("\n   API Endpoint: POST /detect-shape/")
        print("   Health Check: GET /")
        print("\n" + "="*60 + "\n")
        
        try:
            subprocess.run(
                "uvicorn app.main:app --reload --port 8002",
                shell=True
            )
        except KeyboardInterrupt:
            print("\n\n✅ Service stopped")
    
    # Final instructions
    print("""
    \n╔══════════════════════════════════════════════════════════╗
    ║   Next Steps                                              ║
    ╚══════════════════════════════════════════════════════════╝
    
    1. ✅ CLIP model is ready
    2. 🚀 Start service: uvicorn app.main:app --reload --port 8002
    3. 📱 Test with Flutter camera app
    4. 📖 Read CLIP_IMPLEMENTATION_README.md for details
    
    Supported Shapes:
    • 2D: Circle, Square, Triangle, Rectangle, Oval, Pentagon, Hexagon
    • 3D: Cube, Sphere, Cone, Cylinder
    
    API Test:
    curl -X POST "http://localhost:8002/detect-shape/" \\
      -F "image_file=@your_shape_image.jpg"
    """)

if __name__ == "__main__":
    main()
