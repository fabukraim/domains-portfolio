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

    url = 'https://docs.google.com/spreadsheets/d/1PNIvLQsoyh6ssc5wEvtmB4K8eT9tyNmngeyRpa1rFbY/export?format=csv'
    r = requests.get(url)
    r.encoding = 'utf-8'
    f = io.StringIO(r.text)
    cr = csv.reader(f)
    rows = list(cr)
    
    last_row = rows[-1]
    title, slug, category, date, author, excerpt, content = last_row[:7]
    article_url = f"https://domanid.com/articles/{slug}.html"
    
    linkedin_post = generate_linkedin_post(content, article_url)
    
    # Run the exact LinkedIn post payload again inline so we can capture the response text
    url_li = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    author_urn = LINKEDIN_AUTHOR_URN
    if not author_urn.startswith("urn:li:person:"):
        author_urn = f"urn:li:person:{author_urn}"
        
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": linkedin_post or "Test"
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
        response = requests.post(url_li, headers=headers, json=payload, timeout=30)
        with open("error_log.txt", "w", encoding="utf-8") as out:
            out.write(f"Status: {response.status_code}\n")
            out.write(f"Response: {response.text}\n")
            out.write(f"LinkedIn Post Text Used: {linkedin_post}\n")
            out.write(f"Article URL Used: {article_url}\n")
            out.write(f"Token present? {bool(LINKEDIN_ACCESS_TOKEN)}\n")
            out.write(f"URN present? {bool(LINKEDIN_AUTHOR_URN)}\n")
    except Exception as e:
        with open("error_log.txt", "w", encoding="utf-8") as out:
            out.write(f"Exception: {e}\n")

if __name__ == "__main__":
    main()
