import os
import requests

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Set OPENAI_API_KEY terlebih dahulu.")

url = "https://api.openai.com/v1/models"
headers = {"Authorization": f"Bearer {api_key}"}

resp = requests.get(url, headers=headers, timeout=30)
print("Status:", resp.status_code)
print(resp.json())
