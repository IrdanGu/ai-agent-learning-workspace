import os
import json
from dotenv import load_dotenv
from openai import OpenAI
try:
    from agents.calculator_depresi import calculator_depresi
except ImportError:
    from calculator_depresi import calculator_depresi

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# File tempat menyimpan seluruh riwayat percakapan & respon
LOG_FILE = "conversation_timeline.json"


def log_timeline(step_name: str, current_messages: list, api_response=None):
    """
    Menyimpan snapshot alur eksekusi ke file JSON agar bisa diinspeksi.
    """
    timeline_entry = {
        "step": step_name,
        "messages_state": []
    }

    # Konversi setiap pesan ke format dict sederhana
    for m in current_messages:
        if hasattr(m, "model_dump"):
            timeline_entry["messages_state"].append(m.model_dump())
        elif isinstance(m, dict):
            timeline_entry["messages_state"].append(m)
        else:
            timeline_entry["messages_state"].append(str(m))

    if api_response is not None:
        if hasattr(api_response, "model_dump"):
            timeline_entry["api_response"] = api_response.model_dump()
        else:
            timeline_entry["api_response"] = str(api_response)

    # Baca riwayat timeline sebelumnya jika ada
    all_logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                all_logs = json.load(f)
        except Exception:
            all_logs = []

    all_logs.append(timeline_entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(all_logs, f, indent=2, ensure_ascii=False)


# 1. Definisi Fungsi Python Lokal
def get_weather(city: str) -> str:
    data = {
        "jakarta": "Hujan deras, 26°C",
        "surabaya": "Cerah terik, 34°C",
        "bandung": "Sejuk berawan, 21°C"
    }
    return data.get(city.lower(), f"Data cuaca untuk kota '{city}' tidak ditemukan di database.")


# 2. Skema Tool
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Mendapatkan informasi cuaca terkini untuk kota tertentu di Indonesia.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Nama kota, contoh: 'Jakarta', 'Bandung', 'Surabaya'"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator_depresi",
            "description": "Kalkulator Depresiasi Social Battery & Recharging Engine Menghitung konsumsi energi sosial dan estimasi waktu isolasi/pemulihan mandiri.",
            "parameters": {
                "type": "object",
                # argumen (small_talk_count: int, meetings_hours: int, unexpected_calls: int, crowd_hours: int) -> str:
                "properties": {
                    "small_talk_count": {
                        "type": "integer",
                        "description": "Jumlah basa-basi canggung / small talk min_val:0, max_val:30"
                    },
                    "meetings_hours": {
                        "type": "integer",
                        "description": "Durasi meeting / diskusi formal (jam) min_val:0, max_val:12"
                    },
                    "unexpected_calls": {
                        "type": "integer",
                        "description": "Jumlah panggilan telepon / video mendadak min_val:0, max_val:10"
                    },
                    "crowd_hours": {
                        "type": "integer",
                        "description": "Waktu berada di kerumunan publik (jam) min_val:0, max_val:12"
                    }

                }
            }
        }
    }
]

# Reset file log setiap kali skrip dijalankan baru
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

# 3. Pesan Awal dari User
messages = [
    {"role": "user", "content": "Bagaimana kondisi cuaca di jakarta, bandung dan ciamis sekarang?"},
    {"role": "user", "content": "bagaimana kondisi cuaca di kuningan"},
    {"role": "user", "content": "haduh saya melakukan banyak sekali basa basi dengan orang baru sebanyak 10 kali dan sibuk sekali hari ini sampai metting 5 jam, berapa energi saya"}

]

# Rekam Kondisi Awal
log_timeline("01_PERMINTAAN_AWAL_USER", messages)

print("> Langkah 1: Mengirim pertanyaan ke AI...")
response = client.chat.completions.create(
    model="nvidia/nemotron-3.5-super-vl:free",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# Rekam respon API pertama
log_timeline("02_RESPON_PERTAMA_AI (Minta Tool Call)", messages, api_response=response)

msg = response.choices[0].message
print("Finish Reason:", response.choices[0].finish_reason)

if msg.tool_calls:
    print(f"\n> Langkah 2: AI meminta {len(msg.tool_calls)} pemanggilan tool!")

    # PENTING: Masukkan pesan assistant (yang berisi permintaan tool_calls) ke riwayat
    messages.append(msg)
    log_timeline("03_SETELAH_ASSISTANT_TOOL_CALLS_DIMASUKKAN", messages)

    # Eksekusi setiap tool call satu per satu
    for index, tool_call in enumerate(msg.tool_calls, start=1):
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        print(f"  [{index}] Memanggil tool: {func_name}({func_args}) | ID: {tool_call.id}")

        if func_name == "get_weather":
            hasil = get_weather(func_args["city"])
            print(f"      -> Hasil fungsi lokal: {hasil}")

            # Kembalikan hasil eksekusi ke riwayat pesan dengan role 'tool'
            tool_response_msg = {
                "role": "tool",
                "tool_call_id": tool_call.id,  # Menjodohkan hasil ini dengan ID permintaan AI
                "content": hasil
            }
            messages.append(tool_response_msg)
            log_timeline(f"04_SETELAH_TOOL_HASIL_UNTUK_{func_args['city'].upper()}", messages)
        elif func_name == "calculator_depresi":
            # argumen (small_talk_count: int, meetings_hours: int, unexpected_calls: int, crowd_hours: int) -> str:
            hasil = calculator_depresi(func_args["small_talk_count"], func_args["meetings_hours"],
                                       func_args["unexpected_calls"], func_args["crowd_hours"])
            print(f"      -> Hasil fungsi lokal:\n {hasil}")

            tool_response_msg = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": hasil
            }
            messages.append(tool_response_msg)
            log_timeline("04_SETELAH_TOOL_HASIL_CALCULATOR_DEPRESI", messages)

    print("\n> Langkah 3: Mengirim seluruh riwayat percakapan + hasil tools kembali ke AI...")
    response2 = client.chat.completions.create(
        model="nvidia/nemotron-3.5-super-vl:free",
        messages=messages
    )

    # Rekam respon API kedua (final)
    messages.append(response2.choices[0].message)
    log_timeline("05_JAWABAN_AKHIR_AI", messages, api_response=response2)

    print("\n" + "=" * 60)
    print("JAWABAN AKHIR AI:")
    print(response2.choices[0].message.content)
    print("=" * 60)
    print(f"\n[INFO] Seluruh riwayat timeline berhasil direkam ke file '{LOG_FILE}'!")

else:
    print("AI langsung menjawab tanpa memanggil tool:", msg.content)
