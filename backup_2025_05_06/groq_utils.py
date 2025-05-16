import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def get_groq_summary(prompt: str, model: str = "mixtral-8x7b-32768", max_tokens: int = 150) -> str:
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert disaster analyst."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    resp = requests.post(GROQ_API_URL, headers=HEADERS, json=data)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
