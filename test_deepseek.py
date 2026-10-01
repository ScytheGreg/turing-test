import os

import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError("Brak DEEPSEEK_API_KEY w pliku .env")

response = httpx.post(
    "https://api.deepseek.com/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "deepseek-flash",
        "messages": [
            {
                "role": "system",
                "content": "Odpowiadaj krótko po polsku.",
            },
            {
                "role": "user",
                "content": "Cześć! Napisz jedno krótkie zdanie na powitanie.",
            },
        ],
        "stream": False,
    },
    timeout=60,
)

response.raise_for_status()

data = response.json()

print("=== DEEPSEEK ===")
print(data["choices"][0]["message"]["content"])
