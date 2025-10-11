import os
import re

def fix_imports_in_file(filepath):
    """Fix absolute imports to relative imports in a Python file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match 'from src.' imports
    pattern = r'from src\.'
    
    # Calculate relative path based on file location
    relative_path = os.path.relpath('src', os.path.dirname(filepath))
    if relative_path == 'src':
        # File is in src directory, use relative imports
        replacement = 'from .'
    else:
        # File is in subdirectory, calculate proper relative path
        depth = filepath.count('/') - 1  # Subtract 1 for src directory
        if depth == 1:  # File is directly in src/
            replacement = 'from .'
        else:  # File is in subdirectory
            dots = '.' * (depth - 1)
            replacement = f'from {dots}.'
    
    # Replace the imports
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed imports in: {filepath}")
        return True
    return False

# Find all Python files with src imports
files_to_fix = [
    'src/api/v1/endpoints/auth.py',
    'src/api/v1/endpoints/chat.py', 
    'src/api/v1/endpoints/generations.py',
    'src/api/v1/endpoints/users.py',
    'src/api/v1/endpoints/files.py',
    'src/api/dependencies.py',
    'src/core/database.py',
    'src/core/security.py',
    'src/core/seed_data.py',
    'src/models/user.py',
    'src/models/conversation.py',
    'src/models/generation.py',
    'src/models/algorithm.py',
    'src/services/ai_service.py',
    'src/services/generation_service.py',
    'src/services/auth_service.py',
    'src/schemas/user.py',
    'src/schemas/generation.py'
]

fixed_count = 0
for filepath in files_to_fix:
    if os.path.exists(filepath):
        if fix_imports_in_file(filepath):
            fixed_count += 1

print(f"Fixed imports in {fixed_count} files")
