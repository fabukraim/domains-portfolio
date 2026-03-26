import os
import glob

def fix_html_files():
    root_dir = os.getcwd()
    print(f"Working in: {root_dir}")

    # 1. Process root HTML files
    root_htmls = glob.glob(os.path.join(root_dir, "*.html"))
    for filepath in root_htmls:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'app.js' not in content:
            print(f"Fixing root file: {os.path.basename(filepath)}")
            new_content = content.replace('</body>', '    <script src="app.js"></script>\n</body>')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

    # 2. Process articles HTML files
    articles_dir = os.path.join(root_dir, "articles")
    if os.path.exists(articles_dir):
        article_htmls = glob.glob(os.path.join(articles_dir, "*.html"))
        for filepath in article_htmls:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'app.js' not in content:
                print(f"Fixing article file: {os.path.basename(filepath)}")
                new_content = content.replace('</body>', '    <script src="../app.js"></script>\n</body>')
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
    
    print("\nDone! All pages updated.")

if __name__ == "__main__":
    fix_html_files()
