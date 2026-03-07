import requests
import time

# Delete old questions
print("🗑️ Deleting old questions...")
response = requests.delete("http://localhost:8002/api/v1/questions/document/695b4c2b317b98b6846c4665/all")
print(f"   {response.json()}")

# Generate 100% image-based questions
print("\n📸 Generating 100% image-based questions...")
response = requests.post(
    "http://localhost:8002/api/v1/questions/generate",
    json={
        "document_id": "695b4c2b317b98b6846c4665",
        "grade_levels": [1, 2, 3],
        "questions_per_grade": 6,
        "use_rag": False,
        "use_images": True
    }
)
print(f"   {response.json()}")

# Wait for generation
print("\n⏳ Waiting 50 seconds for GPT-4 Vision to analyze images...")
time.sleep(50)

# Check results
print("\n📊 Checking results...")
response = requests.get("http://localhost:8002/api/v1/questions/document/695b4c2b317b98b6846c4665")
questions = response.json()

with_images = sum(1 for q in questions if q.get('image_url'))
without_images = len(questions) - with_images

print(f"\nTotal questions: {len(questions)}")
print(f"✅ With images: {with_images}")
print(f"📝 Without images: {without_images}")

if with_images > 0:
    print("\n📸 Sample image-based questions:")
    for q in [q for q in questions if q.get('image_url')][:3]:
        print(f"\nGrade {q['grade_level']}: {q['question_text']}")
        print(f"   Image: {q['image_url']}")
        print(f"   Answer: {q['correct_answer']}")
