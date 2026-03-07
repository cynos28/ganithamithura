import json
import sys

data = json.load(sys.stdin)

print(f"📊 TOTAL: {len(data)} questions\n")

by_grade = {}
for q in data:
    grade = q['grade_level']
    if grade not in by_grade:
        by_grade[grade] = {'img': 0, 'text': 0}
    
    if q.get('image_url'):
        by_grade[grade]['img'] += 1
    else:
        by_grade[grade]['text'] += 1

for grade in sorted(by_grade.keys()):
    s = by_grade[grade]
    print(f"Grade {grade}: {s['img']} images ✅ | {s['text']} text 📝")

total_img = sum(q.get('image_url') is not None for q in data)
print(f"\n🎯 TOTAL: {total_img} images | {len(data)-total_img} text")
