import os
import re

def fix_relative_imports(filepath):
    """Fix relative imports based on file location"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Get the directory depth from src
    parts = filepath.split('/')
    src_index = parts.index('src')
    depth = len(parts) - src_index - 2  # -2 for src and filename
    
    if depth == 0:  # File is directly in src/
        # Replace patterns like 'from src.core' with 'from .core'
        content = re.sub(r'from src\.', 'from .', content)
    elif depth == 1:  # File is in src/subdir/
        # Replace patterns like 'from src.core' with 'from ..core'
        content = re.sub(r'from src\.', 'from ..', content)
    elif depth == 2:  # File is in src/subdir/subdir/
        # Replace patterns like 'from src.core' with 'from ...core'
        content = re.sub(r'from src\.', 'from ...', content)
    elif depth == 3:  # File is in src/subdir/subdir/subdir/
        # Replace patterns like 'from src.core' with 'from ....core'
        content = re.sub(r'from src\.', 'from ....', content)
    
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
    if fix_relative_imports(filepath):
        fixed_count += 1

print(f"Fixed imports in {fixed_count} files")
