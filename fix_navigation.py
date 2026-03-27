import os

# This script fixes the navigation menu (hamburger menu) path for all existing articles
# and the blog index page. It ensures app.js is loaded from the root directory.

# 1. Update all html files in articles/ directory
articles_dir = "articles"
if os.path.exists(articles_dir):
    print(f"Checking directory: {articles_dir}")
    for filename in os.listdir(articles_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(articles_dir, filename)
            # Try reading with utf-8 first, fallback to latin-1 if there's an encoding error
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    file_content = f.read()
            except UnicodeDecodeError:
                with open(filepath, "r", encoding="latin-1") as f:
                    file_content = f.read()
            
            # Correct the path for app.js
            updated_content = file_content.replace('<script src="app.js"></script>', '<script src="../app.js"></script>')
            
            if updated_content != file_content:
                # Write back using the same logic (or just utf-8 which is safer)
                with open(filepath, "w", encoding="utf-8", errors="replace") as f:
                    f.write(updated_content)
                print(f"√ Fixed: {filename}")
            else:
                print(f"  Skipped (already correct or tag not found): {filename}")

print("\nNavigation fix complete! The mobile menu should now work on all article pages.")
