"""
Test the new 10-class shape classifier model.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from app.services.ai_model.model import get_model_instance, load_model

def test_new_model():
    print("=" * 60)
    print("Testing New 10-Class Shape Classifier Model")
    print("=" * 60)
    
    try:
        # Test loading the new model
        model_path = Path(__file__).parent / "app" / "services" / "ai_model" / "shape_classifier (1).pt"
        
        if not model_path.exists():
            print(f"❌ Model file not found at: {model_path}")
            return False
        
        print(f"✅ Model file found: {model_path.name}\n")
        
        # Load model
        model, class_names = load_model(str(model_path))
        
        print(f"\n📊 Model Configuration:")
        print(f"   - Total Classes: {len(class_names)}")
        print(f"   - Classes: {class_names}")
        print(f"\n✅ New model loaded successfully!")
        print(f"\n📝 Supported Shapes:")
        for i, shape in enumerate(class_names, 1):
            print(f"   {i}. {shape.capitalize()}")
        
        # Test with singleton
        print(f"\n🔄 Testing singleton instance...")
        model2, class_names2, device = get_model_instance()
        
        if len(class_names2) == 10:
            print(f"✅ Singleton working correctly with 10 classes")
        else:
            print(f"⚠️  Singleton has {len(class_names2)} classes (expected 10)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_model()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 New Model Integration Complete!")
        print("=" * 60)
        print("\n📝 Next Steps:")
        print("   1. Restart the backend to load the new model")
        print("   2. Test predictions with the 10-class model")
        print("   3. The model will now detect only these shapes:")
        print("      cuboid, sphere, circle, cone, triangle,")
        print("      pyramid, cube, rectangle, cylinder, square")
    else:
        print("\n❌ Model integration failed. Please check the errors above.")
