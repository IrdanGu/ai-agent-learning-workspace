import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Replace with your values or set in .env
subscription_key = os.getenv("AZURE_VISION_KEY", "")
endpoint = os.getenv("AZURE_VISION_ENDPOINT", "https://my-vision-api-2025.cognitiveservices.azure.com/")

# API endpoint for image analysis
analyze_url = endpoint + "vision/v3.2/analyze"

# Image to analyze (you can use any image URL)
image_url = "https://portal.vision.cognitive.azure.com/dist/assets/portraitProcessing0-BLh3G1UA.png"

headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-Type': 'application/json'
}

params = {
    'visualFeatures': 'Categories,Description,Color,Tags,Objects,Faces',
    'details': 'Landmarks'
}

data = {'url': image_url}

# Make API call
response = requests.post(analyze_url, headers=headers, params=params, json=data)
if not response.ok:
    print(f"Error: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
response.raise_for_status()

# Print results
analysis = response.json()
print(json.dumps(analysis, indent=2))