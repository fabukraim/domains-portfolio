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
            with open(filepath, "r", encoding="utf-8") as f:
                file_content = f.read()
            
            # Correct the path for app.js
            # It replaces <script src="app.js"></script> with <script src="../app.js"></script>
            updated_content = file_content.replace('<script src="app.js"></script>', '<script src="../app.js"></script>')
            
            if updated_content != file_content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                print(f"√ Fixed: {filename}")
            else:
                print(f"  Skipped (already correct or tag not found): {filename}")

print("\nNavigation fix complete! The mobile menu should now work on all article pages.")
