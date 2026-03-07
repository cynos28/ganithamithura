"""
Script to inspect the saved PyTorch model structure.
"""
import torch
from pathlib import Path

model_path = Path(__file__).parent / "app" / "services" / "ai_model" / "shape_classifier.pt"

print(f"Loading model from: {model_path}")
checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)

print("\n" + "=" * 60)
print("Checkpoint Keys:")
print("=" * 60)
for key in checkpoint.keys():
    print(f"  - {key}")

print("\n" + "=" * 60)
print("Model State Dict Keys (first 20):")
print("=" * 60)
state_dict = checkpoint.get("model_state", checkpoint)
for i, key in enumerate(list(state_dict.keys())[:20]):
    print(f"  {i+1}. {key}")

if len(state_dict.keys()) > 20:
    print(f"  ... and {len(state_dict.keys()) - 20} more")

print(f"\n📊 Total parameters: {len(state_dict.keys())}")

if "class_names" in checkpoint:
    print(f"\n📋 Classes: {checkpoint['class_names']}")
else:
    print("\n⚠️  No 'class_names' key found in checkpoint")
