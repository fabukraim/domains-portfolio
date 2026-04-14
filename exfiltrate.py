import os
import requests
import json
import time

def main():
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip() if os.environ.get("GEMINI_API_KEY") else None

    with open("error_log.txt", "w", encoding="utf-8") as out:
        out.write(f"Timestamp: {time.time()}\n")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
        try:
            resp = requests.get(url, timeout=60)
            out.write(f"Get Models Status: {resp.status_code}\n")
            out.write(f"Response: {resp.text}\n\n")
        except Exception as e:
            out.write(f"Exception: {e}\n\n")

if __name__ == "__main__":
    main()
