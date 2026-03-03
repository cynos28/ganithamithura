from app.main import app

print("Shape Service Routes:")
print("=" * 50)
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"{list(route.methods)} {route.path}")
print("=" * 50)
