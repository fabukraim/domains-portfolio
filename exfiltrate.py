import os
import requests
import json
import io
import csv

from blog_generator import generate_linkedin_post, publish_to_linkedin

def main():
    
    url = 'https://docs.google.com/spreadsheets/d/1PNIvLQsoyh6ssc5wEvtmB4K8eT9tyNmngeyRpa1rFbY/export?format=csv'
    r = requests.get(url)
    r.encoding = 'utf-8'
    f = io.StringIO(r.text)
    cr = csv.reader(f)
    rows = list(cr)
    
    # Get the latest article, rows[-1]
    last_row = rows[-1]
    title, slug, category, date, author, excerpt, content = last_row[:7]
    article_url = f"https://domanid.com/articles/{slug}.html"
    
    print(f"Testing with article: {title} - {article_url}")
    
    linkedin_post = generate_linkedin_post(content, article_url)
    if linkedin_post:
        print("Publishing to LinkedIn...")
        success = publish_to_linkedin(linkedin_post, article_url)
        if success:
            print("TEST WAS SUCCESSFUL!")
        else:
            print("Failed to publish to LinkedIn.")
    else:
        print("Failed to generate LinkedIn post.")

if __name__ == "__main__":
    main()
