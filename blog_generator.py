import csv
import os
import requests
import re

# --- CONFIGURATION ---
BLOG_CSV_URL = "https://docs.google.com/spreadsheets/d/1PNIvLQsoyh6ssc5wEvtmB4K8eT9tyNmngeyRpa1rFbY/export?format=csv"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwwn9irH9UZbvX6b25lctzMIPeorl2926QLUfnwO_SxrOy3CnMCG5gtEH-OpSmjhpS5kw/exec"
LOCAL_CSV_PATH = "blog_content.csv"

TEMPLATE_PATH = "article_template.html"
ARTICLES_DIR = "articles"
INDEX_PATH = os.path.join(ARTICLES_DIR, "index.html")

def fetch_csv_data(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        decoded_content = response.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        return my_list
    except Exception as e:
        print(f"Error fetching CSV: {e}")
        return None

def generate_article(row, template):
    # Mapping based on columns: Title, Slug, Category, Date, Author, Excerpt, FullContent, Keywords, ... (Image etc)
    if len(row) < 8:
        print(f"Skipping row due to insufficient columns: {row}")
        return None
    
    # Extract first 8 columns
    title, slug, category, date, author, excerpt, content, keywords = row[:8]
    
    # Image column is at index 8 (9th column)
    image = "https://images.pexels.com/photos/160107/pexels-photo-160107.jpeg" # Default
    if len(row) >= 9 and row[8].strip():
        image = row[8].strip()

    page_content = template
    page_content = page_content.replace("{{TITLE}}", title)
    page_content = page_content.replace("{{SLUG}}", slug)
    page_content = page_content.replace("{{CATEGORY}}", category)
    page_content = page_content.replace("{{DATE}}", date)
    page_content = page_content.replace("{{AUTHOR}}", author)
    page_content = page_content.replace("{{EXCERPT}}", excerpt)
    page_content = page_content.replace("{{CONTENT}}", content)
    page_content = page_content.replace("{{KEYWORDS}}", keywords)
    page_content = page_content.replace("{{IMAGE}}", image)

    filename = f"{slug}.html"
    filepath = os.path.join(ARTICLES_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(page_content)
    
    print(f"Generated: {filepath}")
    return {"title": title, "slug": slug, "date": date, "excerpt": excerpt, "category": category}

def update_index(articles):
    # Load the index.html and update the articles grid
    if not os.path.exists(INDEX_PATH):
        print("articles/index.html not found. Creating a simple one...")
        # (This is handled by the script if we refactor index.html)
        return

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Generate the grid HTML
    grid_html = ""
    for art in articles:
        grid_html += f"""
        <article class="glass-panel">
            <div class="article-content">
                <span class="article-meta">{art['category']} | {art['date']}</span>
                <h2 class="article-title"><a href="{art['slug']}.html">{art['title']}</a></h2>
                <p class="article-excerpt">{art['excerpt']}</p>
            </div>
        </article>"""

    # Replace the content between <!-- START_ARTICLES --> and <!-- END_ARTICLES -->
    pattern = re.compile(r"<!-- START_ARTICLES -->.*?<!-- END_ARTICLES -->", re.DOTALL)
    new_content = pattern.sub(f"<!-- START_ARTICLES -->\n{grid_html}\n<!-- END_ARTICLES -->", content)

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Updated articles/index.html")

def main():
    if not os.path.exists(ARTICLES_DIR):
        os.makedirs(ARTICLES_DIR)

    if not os.path.exists(TEMPLATE_PATH):
        print(f"Error: {TEMPLATE_PATH} not found.")
        return

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    print("Fetching blog data...")
    csv_data = None
    
    if BLOG_CSV_URL and "YOUR_GOOGLE_SHEET_ID_HERE" not in BLOG_CSV_URL:
        csv_data = fetch_csv_data(BLOG_CSV_URL)
    
    if not csv_data:
        print(f"Checking for local CSV: {LOCAL_CSV_PATH}")
        if os.path.exists(LOCAL_CSV_PATH):
            with open(LOCAL_CSV_PATH, "r", encoding="utf-8") as f:
                cr = csv.reader(f)
                csv_data = list(cr)
        else:
            print("Error: No blog source found (Remote or Local).")
            return

    data = csv_data
    if not data:
        return

    csv_rows = list(data)
    articles_data = []
    
    # Mode: Find the FIRST "pending" article and post it (Daily Automation)
    print("Searching for the first 'pending' article...")
    found_any = False
    
    for i, row in enumerate(csv_rows):
        if i == 0: continue # Skip header
        
        # Check if status exists in column 10 (index 9)
        status = "pending"
        if len(row) >= 10:
            status = row[9].strip().lower()
            
        if status == "pending":
            print(f"Found pending article: {row[0]}")
            art = generate_article(row, template)
            if art:
                articles_data.append(art)
                # Update status in Google Sheets
                if APPS_SCRIPT_URL:
                    sheet_row = i + 1
                    print(f"Updating status to 'posted' for row {sheet_row}...")
                    try:
                        resp = requests.get(f"{APPS_SCRIPT_URL}?row={sheet_row}&status=posted")
                        print(f"Status update response: {resp.text}")
                    except Exception as e:
                        print(f"Error updating status: {e}")
                
                found_any = True
                break # ONLY POST ONE PER DAY
    
    if not found_any:
        print("No pending articles found.")
        # Optional: Load all existing articles to rebuild index if needed
        # For now, we only update index if we generated something new.
    
    if articles_data:
        # Note: update_index currently REPLACES the grid. 
        # In a real daily setup, you'd want to prepend or keep the old ones.
        # But since we fetch all rows, we can rebuild the full index from "posted" articles.
        
        # Rebuild full index from all "posted" rows
        all_posted_articles = []
        for i, row in enumerate(csv_rows):
            if i == 0: continue
            status = ""
            if len(row) >= 10: status = row[9].strip().lower()
            
            # If it's the one we JUST posted, or was already posted
            if (found_any and i == (sheet_row - 1)) or status == "posted":
                if len(row) >= 8:
                    all_posted_articles.append({
                        "title": row[0], "slug": row[1], "category": row[2], 
                        "date": row[3], "excerpt": row[5],
                        "image": row[8] if len(row) >= 9 else ""
                    })
        
        if all_posted_articles:
            update_index(all_posted_articles)

if __name__ == "__main__":
    main()
