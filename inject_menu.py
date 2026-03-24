import os
import glob

directory = r'c:\Users\Admin\Desktop\domanid.com'
html_files = glob.glob(os.path.join(directory, '**', '*.html'), recursive=True)

target_ul = '<ul class="nav-links">'
target_logo_end = '</a></div>'
replacement = '''            <div class="menu-toggle" id="mobile-menu">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
            </div>
            <ul class="nav-links">'''

modified_count = 0
for filepath in html_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if target_ul in content and 'id="mobile-menu"' not in content:
            content = content.replace(target_ul, replacement)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            modified_count += 1
    except Exception as e:
        print(f"Failed to process {filepath}: {e}")

print(f'Successfully modified {modified_count} HTML files.')
