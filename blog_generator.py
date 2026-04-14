import csv
import os
import requests
import re
import io
import traceback
import sys
import json
import sys

# --- CONFIGURATION ---
BLOG_CSV_URL = "https://docs.google.com/spreadsheets/d/1PNIvLQsoyh6ssc5wEvtmB4K8eT9tyNmngeyRpa1rFbY/export?format=csv"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwwn9irH9UZbvX6b25lctzMIPeorl2926QLUfnwO_SxrOy3CnMCG5gtEH-OpSmjhpS5kw/exec"
LOCAL_CSV_PATH = "blog_content.csv"

LINKEDIN_ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip() if os.environ.get("LINKEDIN_ACCESS_TOKEN") else None
LINKEDIN_AUTHOR_URN = os.environ.get("LINKEDIN_AUTHOR_URN", "").strip() if os.environ.get("LINKEDIN_AUTHOR_URN") else None
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip() if os.environ.get("GEMINI_API_KEY") else None

TEMPLATE_PATH = "article_template.html"
ARTICLES_DIR = "articles"
INDEX_PATH = os.path.join(ARTICLES_DIR, "index.html")

def fetch_csv_data(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print(f"Connecting to: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        decoded_content = response.content.decode('utf-8')
        
        # Use StringIO to handle multi-line fields correctly
        f = io.StringIO(decoded_content)
        cr = csv.reader(f, delimiter=',')
        my_list = list(cr)
        print(f"Successfully fetched {len(my_list)} rows from CSV.")
        return my_list
    except Exception as e:
        print(f"Error fetching CSV: {e}")
        return None

def generate_article(row, template):
    # Mapping: Title, Slug, Category, Date, Author, Excerpt, FullContent, Keywords, Image, Status
    if len(row) < 8:
        print(f"Skipping row due to insufficient columns: {row}")
        return None
    
    title, slug, category, date, author, excerpt, content, keywords = row[:8]
    
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

def generate_linkedin_post(content, article_url):
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY not found. Skipping LinkedIn summary generation.")
        return None
        
    prompt = f"""
Read the following article and summarize it into an engaging LinkedIn post (between 100 to 150 words maximum to avoid LinkedIn UGC post character limits).
IMPORTANT: THE LINKEDIN POST MUST BE WRITTEN ENTIRELY IN ENGLISH.
Use a professional tone, add a hook (an attention-grabbing first line), and highlight the key points of the article in an interesting way that encourages the reader to read the full article.
CRITICAL NOTE: Do NOT use any Markdown formatting (such as ** for bold or dashes), just plain text and new lines, as LinkedIn does not support it natively.
Add enough spaces and paragraph breaks to make it easy to read, and add appropriate hashtags at the end.
At the end of the post, write a call to action inviting the reader to check the full details via the link.

Article:
{content}
"""
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(api_url, headers={"Content-Type": "application/json"}, json=payload, timeout=60)
        if response.status_code != 200:
            print("Gemini API Error:", response.text)
        response.raise_for_status()
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            generated_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            # Append link
            final_post = generated_text + f"\n\n🔗 Read the full article here:\n{article_url}"
            print("Successfully generated LinkedIn post via Gemini.")
            return final_post
        else:
            print("Unexpected response from Gemini API:", data)
            return None
    except Exception as e:
        print(f"Error generating LinkedIn summary with Gemini: {e}")
        return None

def publish_to_linkedin(text, article_url):
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_AUTHOR_URN:
        print("LinkedIn credentials not found. Skipping publishing.")
        return False
        
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    # User URN format must be urn:li:person:XXXXXX
    author = LINKEDIN_AUTHOR_URN
    if not author.startswith("urn:li:person:"):
        author = f"urn:li:person:{author}"
        
    payload = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "ARTICLE",
                "media": [
                    {
                        "status": "READY",
                        "description": {"text": "Read the full article"},
                        "originalUrl": article_url
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 201:
            print("Successfully published to LinkedIn!")
            return True
        else:
            print(f"Failed to publish to LinkedIn. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error publishing to LinkedIn: {e}")
        return False

def update_index(articles):
    if not os.path.exists(INDEX_PATH):
        print("articles/index.html not found.")
        return

    with open(INDEX_PATH, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

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

    pattern = re.compile(r"<!-- START_ARTICLES -->.*?<!-- END_ARTICLES -->", re.DOTALL)
    new_content = pattern.sub(f"<!-- START_ARTICLES -->\n{grid_html}\n<!-- END_ARTICLES -->", content)

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Updated articles/index.html")

def main():
    try:
        if not os.path.exists(ARTICLES_DIR):
            os.makedirs(ARTICLES_DIR)

        if not os.path.exists(TEMPLATE_PATH):
            print(f"Error: {TEMPLATE_PATH} not found.")
            return

        with open(TEMPLATE_PATH, "r", encoding="utf-8", errors="replace") as f:
            template = f.read()

        print("Fetching blog data...")
        csv_data = None
        if BLOG_CSV_URL:
            csv_data = fetch_csv_data(BLOG_CSV_URL)
        
        if not csv_data:
            if os.path.exists(LOCAL_CSV_PATH):
                with open(LOCAL_CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
                    cr = csv.reader(f)
                    csv_data = list(cr)
            else:
                print("Error: No blog source found.")
                return

        csv_rows = list(csv_data)
        articles_data = []
        found_any = False
        sheet_row = -1
        
        # 1. Post ONE pending article
        for i, row in enumerate(csv_rows):
            if i == 0: continue
            status = "pending"
            if len(row) >= 10:
                status = row[9].strip().lower()
            
            if status == "pending":
                print(f"Found pending article: {row[0]}")
                art = generate_article(row, template)
                if art:
                    articles_data.append(art)
                    
                    # --- Generate and Publish to LinkedIn ---
                    try:
                        full_content = row[6] # Index 6 is the Content based on generate_article mapping
                        article_url = f"https://domanid.com/articles/{art['slug']}.html"
                        print("Generating LinkedIn summary via AI...")
                        linkedin_post = generate_linkedin_post(full_content, article_url)
                        if linkedin_post:
                            print("Publishing to LinkedIn...")
                            publish_to_linkedin(linkedin_post, article_url)
                    except Exception as linkedin_error:
                        print(f"Non-critical Error during LinkedIn publishing: {linkedin_error}")
                    # ---------------------------------------
                    
                    if APPS_SCRIPT_URL:
                        sheet_row = i + 1
                        try:
                            resp = requests.get(f"{APPS_SCRIPT_URL}?row={sheet_row}&status=posted", timeout=30)
                            print(f"Status update response: {resp.text}")
                        except Exception as e:
                            print(f"Error updating status: {e}")
                    found_any = True
                    break

        # 2. Rebuild index (latest first)
        print("Rebuilding articles/index.html...")
        all_posted_articles = []
        for i, row in enumerate(csv_rows):
            if i == 0: continue
            status = ""
            if len(row) >= 10:
                status = row[9].strip().lower()
            
            if (found_any and i == (sheet_row - 1)) or status == "posted":
                if len(row) >= 8:
                    expected_filepath = os.path.join(ARTICLES_DIR, f"{row[1]}.html")
                    if os.path.exists(expected_filepath):
                        all_posted_articles.append({
                            "title": row[0], "slug": row[1], "category": row[2], 
                            "date": row[3], "excerpt": row[5]
                        })
                    else:
                        print(f"Skipping {row[1]} from index: HTML file was manually deleted.")
        
        if all_posted_articles:
            all_posted_articles.reverse() # SORT: LATEST FIRST
            update_index(all_posted_articles)

    except Exception as e:
        print("--- CRITICAL ERROR ---")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
