from openai import OpenAI
import os
import sys

# Setup warna untuk terminal (opsional, biar keren)
_USE_COLOR = sys.stdout.isatty() and os.getenv("NO_COLOR") is None
_REASONING_COLOR = "\033[90m" if _USE_COLOR else ""
_RESET_COLOR = "\033[0m" if _USE_COLOR else ""

# Konfigurasi Client ke NVIDIA NIM
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

print("Sedang menghubungi NVIDIA NIM... (Model: z-ai/glm4.7)\n")

try:
    completion = client.chat.completions.create(
        model="z-ai/glm4.7",
        messages=[{"role": "user", "content": "jelaskan apa itu gajah?"}],
        temperature=0.7,
        top_p=0.7,
        max_tokens=1024,
        stream=True
    )

    print("Respon AI:\n" + "-" * 20)

    # Loop untuk menangkap stream respon
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

    print("\n" + "-" * 20 + "\nSukses! API berfungsi.")

except Exception as e:
    print(f"\nError terjadi: {e}")
    print("\nKemungkinan penyebab:")
    print("1. API Key salah/sudah dihapus.")
    print("2. Nama model salah (cek lagi di dashboard NVIDIA).")
    print("3. Koneksi internet bermasalah.")