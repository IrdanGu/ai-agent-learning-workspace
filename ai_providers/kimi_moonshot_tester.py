import os
import requests
import json
import sys
from dotenv import load_dotenv

load_dotenv()

# ============================================================
#  API KEY DIMUAT DARI .env ATAU ENVIRONMENT VARIABLE
# ============================================================
API_KEY = os.getenv("KIMI_API_KEY", os.getenv("MOONSHOT_API_KEY", "YOUR_API_KEY_HERE"))
BASE_URL = "https://api.kimi.com/coding/v1/messages"
MODEL = "kimi-for-coding"
# ============================================================


def print_separator(title=""):
    print("\n" + "=" * 50)
    if title:
        print(f"  {title}")
        print("=" * 50)


def test_basic_connection():
    """Test 1: Cek apakah API bisa diakses (tanpa streaming)"""
    print_separator("TEST 1: Basic Connection")

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "max_tokens": 50,
        "system": "You are a helpful assistant.",
        "messages": [
            {"role": "user", "content": "Say exactly: API OK"}
        ],
        "stream": False,
    }

    try:
        print(f"  Connecting to: {BASE_URL}")
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=15)

        print(f"  Status Code : {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Response    : ✅ SUCCESS")

            # Coba ambil teks dari response
            try:
                text = data["content"][0]["text"]
                print(f"  Model reply : {text}")
            except (KeyError, IndexError):
                print(f"  Raw JSON    : {json.dumps(data, indent=2)}")

            return True

        elif response.status_code == 401:
            print("  Response    : ❌ UNAUTHORIZED — API Key salah atau expired")
            print(f"  Detail      : {response.text}")
            return False

        elif response.status_code == 403:
            print("  Response    : ❌ FORBIDDEN — API Key tidak punya akses")
            print(f"  Detail      : {response.text}")
            return False

        else:
            print(f"  Response    : ❌ ERROR {response.status_code}")
            print(f"  Detail      : {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("  Response    : ❌ CONNECTION ERROR — Tidak bisa terhubung ke server")
        return False
    except requests.exceptions.Timeout:
        print("  Response    : ❌ TIMEOUT — Server tidak merespons dalam 15 detik")
        return False
    except Exception as e:
        print(f"  Response    : ❌ UNEXPECTED ERROR — {e}")
        return False


def test_streaming():
    """Test 2: Cek apakah streaming berjalan"""
    print_separator("TEST 2: Streaming")

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "max_tokens": 100,
        "system": "You are a helpful assistant.",
        "messages": [
            {"role": "user", "content": "Count from 1 to 5, one number per word."}
        ],
        "stream": True,
    }

    try:
        print("  Sending streaming request...")
        response = requests.post(
            BASE_URL, headers=headers, json=payload, stream=True, timeout=20
        )

        print(f"  Status Code : {response.status_code}")

        if response.status_code == 200:
            print("  Streaming   : ✅ Connected — receiving chunks:")
            print("  ", end="", flush=True)

            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data:"):
                        raw = decoded[5:].strip()
                        if raw == "[DONE]":
                            break
                        try:
                            chunk = json.loads(raw)
                            # Anthropic-style delta
                            delta = (
                                chunk.get("delta", {}).get("text", "")
                                or chunk.get("content", [{}])[0].get("text", "")
                            )
                            if delta:
                                print(delta, end="", flush=True)
                                chunk_count += 1
                        except json.JSONDecodeError:
                            pass

            print(f"\n  Chunks      : {chunk_count} text chunks received")
            return True
        else:
            print(f"  Streaming   : ❌ FAILED ({response.status_code})")
            print(f"  Detail      : {response.text}")
            return False

    except Exception as e:
        print(f"  Streaming   : ❌ ERROR — {e}")
        return False


def test_response_path():
    """Test 3: Verifikasi response path untuk Pluely"""
    print_separator("TEST 3: Response Path (untuk Pluely)")

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "max_tokens": 50,
        "system": "You are a helpful assistant.",
        "messages": [{"role": "user", "content": "Reply with one word: Hello"}],
        "stream": False,
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=15)

        if response.status_code == 200:
            data = response.json()
            print("  Full JSON response structure:")
            print(json.dumps(data, indent=4))

            # Cek path umum
            paths = {
                "content[0].text": lambda d: d["content"][0]["text"],
                "choices[0].message.content": lambda d: d["choices"][0]["message"]["content"],
            }

            print("\n  Path check:")
            for path, accessor in paths.items():
                try:
                    value = accessor(data)
                    print(f"  ✅ '{path}' → '{value}'")
                except (KeyError, IndexError, TypeError):
                    print(f"  ❌ '{path}' → tidak ditemukan")

    except Exception as e:
        print(f"  ❌ ERROR — {e}")


def main():
    print_separator("KIMI CODE API TESTER")
    print(f"  Model  : {MODEL}")
    print(f"  URL    : {BASE_URL}")
    key_preview = API_KEY[:10] + "..." if len(API_KEY) > 10 else API_KEY
    print(f"  APIKey : {key_preview}")

    if API_KEY == "YOUR_API_KEY_HERE":
        print("\n  ⚠️  Ganti API_KEY di baris 8 dengan API key kamu dulu!")
        sys.exit(1)

    results = []
    results.append(test_basic_connection())
    results.append(test_streaming())
    test_response_path()

    print_separator("SUMMARY")
    print(f"  Basic Connection : {'✅ PASS' if results[0] else '❌ FAIL'}")
    print(f"  Streaming        : {'✅ PASS' if results[1] else '❌ FAIL'}")

    if all(results):
        print("\n  🎉 Semua test passed! API kamu berjalan dengan baik.")
        print("  Response Path untuk Pluely: content[0].text")
    else:
        print("\n  ⚠️  Ada test yang gagal. Cek detail di atas.")


if __name__ == "__main__":
    main()