import json
import re

# Read the JSON file
with open('data/activities_level1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Fix all "answer" to "correct_answer" in read questions
# and remove duplicate options
for number_key in data['numbers']:
    number_data = data['numbers'][number_key]
    
    if 'read' in number_data and 'questions' in number_data['read']:
        for question in number_data['read']['questions']:
            # Fix field naming: answer -> correct_answer
            if 'answer' in question:
                question['correct_answer'] = question.pop('answer')
            
            # Fix duplicate options
            if 'options' in question:
                # Remove duplicates while preserving order
                seen = set()
                unique_options = []
                for opt in question['options']:
                    if opt not in seen:
                        seen.add(opt)
                        unique_options.append(opt)
                
                # If we removed duplicates, add new unique option
                if len(unique_options) < len(question['options']):
                    # Get the correct answer to ensure it's in options  
                    correct_ans = question.get('correct_answer')
                    
                    # Add a sensible new option based on number context
                    number = int(number_key)
                    if question['type'] == 'word_to_digit':
                        # For number questions, add adjacent numbers
                        potential_options = [str(number-1), str(number), str(number+1), str(number+2)]
                    elif question['type'] == 'digit_to_word':
                        # For word questions, add number words
                        words = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']
                        potential_options = [words[number-1] if number > 0 else 'zero', 
                                            words[number] if number <= 12 else str(number),
                                            words[number+1] if number+1 <= 12 else str(number+1)]
                    else:
                        # Mixed type
                        potential_options = [str(number-1), str(number), str(number+1)]
                    
                    # Add missing option that's not already in unique_options
                    for opt in potential_options:
                        if opt not in unique_options and len(unique_options) < 4:
                            unique_options.append(opt)
                            break
                    
                    question['options'] = unique_options

# Write back to file  
with open('data/activities_level1.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Fixed all issues in activities_level1.json!")
print("   - Changed all 'answer' fields to 'correct_answer'")
print("   - Removed duplicate options and added appropriate alternatives")
