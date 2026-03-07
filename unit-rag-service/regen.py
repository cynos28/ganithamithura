import requests
import time

DOC_ID = "695b4c2b317b98b6846c4665"

# Delete old questions
r = requests.delete(f"http://localhost:8002/api/v1/questions/document/{DOC_ID}/all")
print("🗑️  Deleted:", r.json().get("questions_deleted"), "questions")

# Generate fresh 100% image-based questions
r = requests.post("http://localhost:8002/api/v1/questions/generate", json={
    "document_id": DOC_ID,
    "grade_levels": [1, 2, 3],
    "questions_per_grade": 6,
    "use_rag": False,
    "use_images": True
})
print("🚀 Started:", r.json().get("message"))
print("⏳ Waiting 65s for 18 images to be analyzed by GPT-4 Vision...")
time.sleep(65)

# Check results
qs = requests.get(f"http://localhost:8002/api/v1/questions/document/{DOC_ID}").json()
imgs = [q.get("image_url") for q in qs]
unique_imgs = set(i for i in imgs if i)

print(f"\n📊 Total questions : {len(qs)}")
print(f"✅ All have images : {all(i is not None for i in imgs)}")
print(f"🖼️  Unique images   : {len(unique_imgs)} used")
print()
print("Grade | Image file          | Question")
print("-" * 80)
for q in qs:
    img = q.get("image_url", "").split("/")[-1] if q.get("image_url") else "NONE"
    print(f"  {q['grade_level']}   | {img:<20} | {q['question_text'][:55]}")
