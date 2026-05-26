import os
import sys

# Ensure UTF-8 output encoding if possible
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def print_tree(startpath):
    exclude_dirs = {'.git', '__pycache__', '.streamlit', 'uploads', '.gemini'}
    output = []
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = '  ' * level
        sub_folder = os.path.basename(root)
        if sub_folder:
            output.append(f"{indent}[DIR] {sub_folder}/  -->  {os.path.abspath(root)}")
        
        sub_indent = '  ' * (level + 1)
        for f in sorted(files):
            file_path = os.path.join(root, f)
            output.append(f"{sub_indent}[FILE] {f}  -->  {os.path.abspath(file_path)}")
            
    return '\n'.join(output)

if __name__ == '__main__':
    project_root = r"d:\A_LMS"
    print(print_tree(project_root))
