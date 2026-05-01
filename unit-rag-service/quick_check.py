#!/usr/bin/env python3
import requests

response = requests.get("http://localhost:8002/api/v1/questions/document/695b4c2b317b98b6846c4665")
questions = response.json()

with_images = [q for q in questions if q.get('image_url')]
without_images = [q for q in questions if not q.get('image_url')]

print(f"📊 TOTAL: {len(questions)} questions")
print(f"✅ With images: {len(with_images)}")
print(f"📝 Without images: {len(without_images)}")

if len(with_images) > 0:
    print("\n📸 Sample image questions:")
    for q in with_images[:3]:
        print(f"\n• {q['question_text']}")
        print(f"  Image: {q['image_url']}")
