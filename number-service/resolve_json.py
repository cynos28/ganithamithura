import re

def resolve_conflicts(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to match the HEAD branch logic
    # We want to keep whatever is between <<<<<<< HEAD and =======
    # and discard ======= to >>>>>>> feature/shape_int
    
    # We use re.DOTALL to match across newlines
    pattern = re.compile(r'<<<<<<< HEAD\n(.*?)\n=======\n.*?\n>>>>>>> feature/shape_int\n', re.DOTALL)
    
    resolved_content = pattern.sub(r'\1\n', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(resolved_content)

resolve_conflicts('data/activities_level1.json')
resolve_conflicts('data/activities_level2.json')
print("Conflicts resolved for both json files!")
