import os
import requests
import json
import time

def main():
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip() if os.environ.get("GEMINI_API_KEY") else None

    with open("error_log.txt", "w", encoding="utf-8") as out:
        out.write(f"Timestamp: {time.time()}\n")
        models_to_try = [
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-pro",
            "gemini-1.5-pro-latest"
        ]
        
        prompt = "Hello, generate 5 words."
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=60)
                out.write(f"Model: {model} => Status: {resp.status_code}\n")
                out.write(f"Response: {resp.text}\n\n")
            except Exception as e:
                out.write(f"Model: {model} => Exception: {e}\n\n")

if __name__ == "__main__":
    main()
