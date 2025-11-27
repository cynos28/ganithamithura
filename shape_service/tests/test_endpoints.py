from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_detect_shape():
    with open("tests/test_image.png", "rb") as f:
        response = client.post("/shapes-patterns/detect-shape/", files={"image_file": ("test_image.png", f, "image/png")})
    assert response.status_code == 200
    assert "shape" in response.json()
