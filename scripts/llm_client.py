import os
import time
from pathlib import Path
import json

# .env yukle
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    for line in open(env_path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

def ask_llm(prompt: str, system: str = "", retries: int = 3, delay: int = 5) -> str:
    import requests
    
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        print("Warning: GROQ_API_KEY is missing in .env file!")
        return ""
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.0
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                time.sleep(1.5) # limit korumasi
                return response.json()["choices"][0]["message"]["content"].strip()
            elif response.status_code == 429:
                print(f"[Groq limit] 5s bekliyor (Deneme {attempt+1}/{retries})")
                time.sleep(5)
            else:
                print(f"Groq API Error: {response.status_code} - {response.text}")
                time.sleep(delay)
        except Exception as e:
            print(f"Baglanti hatasi: {e}")
            time.sleep(delay)
            
    return ""