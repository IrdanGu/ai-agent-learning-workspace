import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
model = "nvidia/nemotron-3.5-super-vl:free"

client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

response = client.responses.create(
    model=model,
    instructions="You are a coding assistant that talks like a pirate.",
    input="explain to me what rest api is?",
)

completion = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "Bicara seperti bajak laut."},
        {"role": "user", "content": "Halo, apa kabar?"}
    ]
)
# Mengambil teks harus melewati .choices[0].message:
# simpan semua ouput dari completion di file yang terstruktur sebagai JSON
with open("output.json", "w", encoding="utf-8") as file:
    file.write(completion.model_dump_json(indent=2))

# conversi ke json
with open("output.json", "r", encoding="utf-8") as file:
    output = file.read()
output_json = json.loads(output)

