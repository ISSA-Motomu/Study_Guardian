import re

file_path = 'c:/Family/Study_Guadian/blueprints/web.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find the endpoint definition
pattern = r'(@web_bp\.route\(\"/api/admin/users\")'
parts = re.split(pattern, content)

if len(parts) > 3:  # Means we have at least 2 occurrences (part0, match1, part1, match2, part2)
    print('Duplicate found. Fixing...')
    # Keep up to the end of the first implementation (approx heuristic or just keep first)
    # Actually, let's look at the structure.
    # We want to keep everything up to the START of the second occurrence.
    
    # Calculate index of second occurrence
    first_idx = content.find('@web_bp.route("/api/admin/users")')
    if first_idx != -1:
        second_idx = content.find('@web_bp.route("/api/admin/users")', first_idx + 1)
        if second_idx != -1:
             new_content = content[:second_idx]
             # Trim trailing newlines and ensure one newline at EOF
             new_content = new_content.rstrip() + '\n'
             with open(file_path, 'w', encoding='utf-8') as f:
                 f.write(new_content)
             print('File fixed.')
        else:
             print('Only one occurrence found (via index check).')
    else:
        print('No occurrence found.')

else:
    print('No duplicates found (via split check).')
