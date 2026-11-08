import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LONGCAT_API_KEY", "")
url = "https://api.longcat.chat/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "LongCat-Flash-Lite",
    "messages": [
        {"role": "user", "content": "Hello, please introduce yourself."}
    ],
    "max_tokens": 1000,
    "temperature": 0.7
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
