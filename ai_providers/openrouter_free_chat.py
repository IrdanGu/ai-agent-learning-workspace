import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")


URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "nvidia/nemotron-3.5-super-vl:free"


def get_message(api_key, messages):
    response = requests.post(
        URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": MODEL, "messages": messages, "reasoning": {"enabled": True}},
        timeout=60,
    )
    try:
        body = response.json()
    except ValueError:
        raise ValueError(f"OpenRouter returned HTTP {response.status_code} with an invalid JSON response") from None

    if not response.ok or (isinstance(body, dict) and body.get("error")):
        error = body.get("error") if isinstance(body, dict) else None
        message = error.get("message") if isinstance(error, dict) else error
        raise ValueError(f"OpenRouter error (HTTP {response.status_code}): {message or 'Unknown API error'}")

    try:
        message = body["choices"][0]["message"]
        if not isinstance(message, dict):
            raise TypeError
    except (KeyError, IndexError, TypeError):
        raise ValueError("OpenRouter returned an unexpected response without an assistant message") from None
    return message


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Set the OPENROUTER_API_KEY environment variable to your OpenRouter API key")

    messages = [{"role": "user", "content": "How many r's are in the word 'strawberry'?"}]
    first = get_message(api_key, messages)
    print(first.get("content") or "")
    assistant_message = {"role": "assistant", "content": first.get("content")}
    if "reasoning_details" in first:
        assistant_message["reasoning_details"] = first["reasoning_details"]
    messages.extend([assistant_message, {"role": "user", "content": "Are you sure? Think carefully."}])
    second = get_message(api_key, messages)
    print(second.get("content") or "")


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)