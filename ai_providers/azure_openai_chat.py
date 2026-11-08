import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
    api_version="2024-10-21", # Standard API version for Azure OpenAI
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://my-openai-api-2025.openai.azure.com/"),
)

# IMPORTANT: The 'model' parameter below must be the DEPLOYMENT NAME 
# you chose when deploying the model in Azure OpenAI Studio.
# Common deployment names are often the same as the model name, e.g., "gpt-4o-mini"
response = client.chat.completions.create(   
  model="gpt-4o-mini", # <--- CHANGE THIS to your actual Deployment Name
  messages=[{"role": "user", "content": "This is a test."}],
)

print(response.model_dump_json(indent=2))