import os
import re

def fix_to_absolute_imports(filepath):
    """Fix relative imports back to absolute imports"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace relative imports with absolute imports
    content = re.sub(r'from \.\.\.', 'from src.', content)
    content = re.sub(r'from \.\.', 'from src.', content)
    content = re.sub(r'from \.', 'from src.', content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed imports in: {filepath}")
        return True
    return False

# Find all Python files in src directory
def find_python_files(directory):
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                python_files.append(os.path.join(root, file))
    return python_files

# Fix all files
python_files = find_python_files('src')
fixed_count = 0

for filepath in python_files:
    if fix_to_absolute_imports(filepath):
        fixed_count += 1

print(f"Fixed imports in {fixed_count} files")
