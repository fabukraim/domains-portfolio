import os
import requests
import json
import io
import csv

from blog_generator import generate_linkedin_post, publish_to_linkedin

def main():
    LINKEDIN_ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip() if os.environ.get("LINKEDIN_ACCESS_TOKEN") else None
    LINKEDIN_AUTHOR_URN = os.environ.get("LINKEDIN_AUTHOR_URN", "").strip() if os.environ.get("LINKEDIN_AUTHOR_URN") else None
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip() if os.environ.get("GEMINI_API_KEY") else None

    with open("error_log.txt", "w", encoding="utf-8") as out:
        out.write("Testing Gemini\n")
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": "Hello, generate 5 words."}]}]
            }
            resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=60)
            out.write(f"Gemini Status: {resp.status_code}\n")
            out.write(f"Gemini Response: {resp.text}\n")
        except Exception as e:
            out.write(f"Gemini Exception: {e}\n")

        # Now test actual function
        url_csv = 'https://docs.google.com/spreadsheets/d/1PNIvLQsoyh6ssc5wEvtmB4K8eT9tyNmngeyRpa1rFbY/export?format=csv'
        r = requests.get(url_csv)
        r.encoding = 'utf-8'
        cr = csv.reader(io.StringIO(r.text))
        rows = list(cr)
        last_row = rows[-1]
        title, slug, category, date, author, excerpt, content = last_row[:7]
        article_url = f"https://domanid.com/articles/{slug}.html"
        
        post = generate_linkedin_post(content, article_url)
        out.write(f"generate_linkedin_post returned: {post}\n")
        
        if post:
            suc = publish_to_linkedin(post, article_url)
            out.write(f"Publish_to_linkedin returned: {suc}\n")

if __name__ == "__main__":
    main()
