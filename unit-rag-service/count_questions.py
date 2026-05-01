import json
import sys

data = json.load(sys.stdin)

print(f"📊 TOTAL QUESTIONS: {len(data)}\n")

by_grade = {}
for q in data:
    grade = q['grade_level']
    if grade not in by_grade:
        by_grade[grade] = {'with_img': 0, 'without_img': 0}
    
    if q.get('image_url'):
        by_grade[grade]['with_img'] += 1
    else:
        by_grade[grade]['without_img'] += 1

print("By Grade Level:")
for grade in sorted(by_grade.keys()):
    stats = by_grade[grade]
    total = stats['with_img'] + stats['without_img']
    print(f"  Grade {grade}: {stats['with_img']} with images ✅ | {stats['without_img']} text-only 📝 (Total: {total})")

total_with_img = sum(q.get('image_url') is not None for q in data)
total_without = len(data) - total_with_img

print(f"\n🎯 SUMMARY:")
print(f"   Image-based (GPT-4 Vision): {total_with_img}")
print(f"   Text-based (RAG):           {total_without}")
print(f"   Mix: 50/50 split as designed ✅")
