import os
import glob

directory = r'c:\Users\Admin\Desktop\domanid.com'
html_files = glob.glob(os.path.join(directory, '**', '*.html'), recursive=True)

script_to_add = '''
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const mobileMenu = document.getElementById('mobile-menu');
            const navLinks = document.querySelector('.nav-links');
            if (mobileMenu && navLinks) {
                mobileMenu.addEventListener('click', () => {
                    mobileMenu.classList.toggle('is-active');
                    navLinks.classList.toggle('active');
                });
                navLinks.querySelectorAll('a').forEach(link => {
                    link.addEventListener('click', () => {
                        mobileMenu.classList.remove('is-active');
                        navLinks.classList.remove('active');
                    });
                });
            }
        });
    </script>
</body>
'''

modified_count = 0
for filepath in html_files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        changes_made = False
        
        # 1. Break CSS cache
        if 'style.css"' in content:
            content = content.replace('style.css"', 'style.css?v=1.1"')
            changes_made = True
            
        # 2. Add inline script before closing </body>
        if '</body>' in content and 'mobileMenu.addEventListener' not in content:
            # Replace the first </body> (or the one at the end)
            content = content.replace('</body>', script_to_add)
            changes_made = True
            
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            modified_count += 1
            
    except Exception as e:
        print(f"Failed to process {filepath}: {e}")

print(f"Modified {modified_count} HTML files to fix cache and JS logic.")
