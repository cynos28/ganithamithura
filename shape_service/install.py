#!/usr/bin/env python3
"""
Installation script for CLIP Shape Detection
Ensures all dependencies are properly installed
"""
import subprocess
import sys

def run_pip_install():
    """Install dependencies from pyproject.toml"""
    print("📦 Installing dependencies...")
    
    try:
        # Install in editable mode
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
            return True
        else:
            print(f"❌ Installation failed:\n{result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return False

def verify_imports():
    """Verify all required packages can be imported"""
    print("\n🔍 Verifying installations...")
    
    required_packages = [
        ("numpy", "NumPy"),
        ("PIL", "Pillow"),
        ("transformers", "Transformers"),
        ("torch", "PyTorch"),
        ("requests", "Requests"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
    ]
    
    all_ok = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - Not installed")
            all_ok = False
    
    return all_ok

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║   CLIP Shape Detection - Installation                    ║
╚══════════════════════════════════════════════════════════╝
""")
    
    print(f"🐍 Python: {sys.version}\n")
    
    # Install dependencies
    if not run_pip_install():
        print("\n❌ Installation failed. Please check errors above.")
        return 1
    
    # Verify installations
    if not verify_imports():
        print("\n⚠️  Some packages failed to import.")
        print("Try running: pip install -e . --force-reinstall")
        return 1
    
    print("""
\n✅ Installation Complete!

Next Steps:
1. Test the model:
   python test_clip_detection.py

2. Start the service:
   uvicorn app.main:app --reload --port 8002

3. Test the API:
   python test_api.py

4. Read the docs:
   - IMPLEMENTATION_COMPLETE.md
   - CLIP_IMPLEMENTATION_README.md

The CLIP model (~600MB) will download automatically on first use.
""")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
