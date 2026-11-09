"""
Autonomous Agent Workflow Loop (Multi-Turn Function Calling & Timeline Logger)
=============================================================================
Skrip ini mengimplementasikan siklus agen otonom (Agentic While-Loop) dengan
kemampuan:
1. Menangani pemanggilan tool bertahap (multi-turn tool calling) hingga tuntas.
2. Selalu menyertakan definisi tools di setiap turn API request.
3. Fallback parser untuk menangkap format teks manual <tool_call> jika model
   menghasilkan XML/teks biasa bukan JSON structured tool_calls.
4. Perekaman timeline visual ke JSON untuk audit proses penalaran agen.
"""

import os
import sys
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

# Pastikan output terminal Windows aman untuk karakter UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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

LOG_FILE = "agents/agent_loop_timeline.json" if os.path.exists("agents") else "agent_loop_timeline.json"


# ==============================================================================
# 1. DEFINISI FUNGSI TOOLS
# ==============================================================================

def get_weather(city: str) -> str:
    """Mengembalikan data simulasi cuaca kota."""
    data = {
        "jakarta": "Hujan deras, 26°C",
        "surabaya": "Cerah terik, 34°C",
        "bandung": "Sejuk berawan, 21°C",
        "ciamis": "Hujan ringan, 24°C",
        "kuningan": "Kabut sejuk, 20°C"
    }
    return data.get(city.lower().strip(), f"Data cuaca untuk '{city}' tidak tersedia dalam database.")


def tool_calculator_depresi(small_talk_count: int = 0, meetings_hours: int = 0,
                            unexpected_calls: int = 0, crowd_hours: int = 0) -> str:
    """Wrapper untuk kalkulator energi baterai sosial."""
    return calculator_depresi(
        small_talk_count=small_talk_count,
        meetings_hours=meetings_hours,
        unexpected_calls=unexpected_calls,
        crowd_hours=crowd_hours
    )


# Registry fungsi Python lokal
TOOL_REGISTRY = {
    "get_weather": lambda args: get_weather(args.get("city", "")),
    "calculator_depresi": lambda args: tool_calculator_depresi(
        small_talk_count=args.get("small_talk_count", 0),
        meetings_hours=args.get("meetings_hours", 0),
        unexpected_calls=args.get("unexpected_calls", 0),
        crowd_hours=args.get("crowd_hours", 0)
    )
}

# Skema tools untuk dikirim ke API LLM
TOOLS = [
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
                        "description": "Nama kota, contoh: 'Jakarta', 'Bandung', 'Ciamis', 'Kuningan'"
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
            "description": "Menghitung konsumsi energi sosial (social battery) dan rekomendasi durasi me-time/recharging.",
            "parameters": {
                "type": "object",
                "properties": {
                    "small_talk_count": {
                        "type": "integer",
                        "description": "Jumlah obrolan basa-basi atau small talk yang dilakukan."
                    },
                    "meetings_hours": {
                        "type": "integer",
                        "description": "Total jam meeting / rapat formal hari ini."
                    },
                    "unexpected_calls": {
                        "type": "integer",
                        "description": "Jumlah panggilan telepon/video call mendadak."
                    },
                    "crowd_hours": {
                        "type": "integer",
                        "description": "Berapa jam berada di tempat kerumunan umum."
                    }
                }
            }
        }
    }
]


# ==============================================================================
# 2. LOGGING TIMELINE
# ==============================================================================

def log_timeline(step_name: str, current_messages: list, api_response=None):
    """Menyimpan snapshot proses penalaran dan eksekusi pesan ke JSON."""
    timeline_entry = {
        "step": step_name,
        "messages_state": []
    }

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

    timeline_data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                timeline_data = json.load(f)
        except Exception:
            timeline_data = []

    timeline_data.append(timeline_entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(timeline_data, f, indent=2, ensure_ascii=False)


# ==============================================================================
# 3. FALLBACK XML TOOL PARSER (Untuk Model yang Mencetak Teks <tool_call>)
# ==============================================================================

def parse_xml_tool_calls(text: str):
    """
    Mendeteksi pemanggilan tool manual berformat XML jika model
    tidak mengembalikannya dalam struktur tool_calls resmi.
    Contoh:
      <tool_call>
      <function=get_weather>
      <parameter=city>Bandung</parameter>
      </function>
      </tool_call>
    """
    if not text or "<tool_call>" not in text:
        return []

    calls = []
    blocks = re.findall(r"<tool_call>(.*?)</tool_call>", text, re.DOTALL)
    for block in blocks:
        func_match = re.search(r"<function=([a-zA-Z0-9_]+)>", block)
        if not func_match:
            continue
        func_name = func_match.group(1)

        args = {}
        param_matches = re.findall(r"<parameter=([a-zA-Z0-9_]+)>\s*(.*?)\s*</parameter>", block, re.DOTALL)
        for p_name, p_val in param_matches:
            val = p_val.strip()
            # Coba konversi angka
            if val.isdigit():
                val = int(val)
            args[p_name] = val

        calls.append({
            "name": func_name,
            "arguments": args
        })
    return calls


# ==============================================================================
# 4. AGENTIC WHILE LOOP RUNNER
# ==============================================================================

def run_agent_loop(user_prompt: str, max_iterations: int = 8, model: str = "nvidia/nemotron-3.5-super-vl:free"):
    """
    Menjalankan alur otonom:
    Model meminta tools -> Eksekusi tools -> Kembalikan hasil -> Model analisa lagi
    Loop berulang sampai Model menyatakan jawaban selesai (finish).
    """
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    messages = [
        {
            "role": "system",
            "content": (
                "Kamu adalah asisten cerdas yang memiliki akses ke berbagai tools. "
                "Gunakan tool yang relevan untuk menjawab kebutuhan pengguna. "
                "Jika pengguna menanyakan beberapa hal (misalnya cuaca beberapa kota dan status energi), "
                "kamu dapat memanggil tool secara bertahap atau sekaligus sampai semua data lengkap. "
                "Setelah semua informasi terkumpul, susun jawaban akhir yang ramah, rapi, dan komprehensif."
            )
        },
        {"role": "user", "content": user_prompt}
    ]

    log_timeline("01_PERMINTAAN_AWAL_USER", messages)
    print(f"\n[USER PROMPT]: {user_prompt}\n" + "=" * 60)

    step = 1
    while step <= max_iterations:
        print(f"\n>>> [PUTARAN KE-{step}]: Mengirim riwayat ke LLM...")

        # PENTING: tools=TOOLS selalu disertakan di setiap putaran!
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        msg = response.choices[0].message
        finish_reason = response.choices[0].finish_reason
        print(f"    Finish Reason: {finish_reason}")

        # Simpan assistant message ke riwayat
        messages.append(msg)
        log_timeline(f"STEP_{step:02d}_ASSISTANT_REPLY", messages, api_response=response)

        # KASUS A: Native Tool Calls (OpenAI Structured Tool Calling)
        if msg.tool_calls:
            print(f"    -> AI meminta {len(msg.tool_calls)} Native Tool Call(s):")
            for tc in msg.tool_calls:
                fn_name = tc.function.name
                try:
                    fn_args = json.loads(tc.function.arguments)
                except Exception:
                    fn_args = {}

                print(f"       * Eksekusi {fn_name}({fn_args}) [ID: {tc.id}]")
                if fn_name in TOOL_REGISTRY:
                    result = TOOL_REGISTRY[fn_name](fn_args)
                else:
                    result = f"Error: Tool '{fn_name}' tidak ditemukan."

                print(f"         Hasil: {str(result).strip()[:100]}...")

                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(result)
                }
                messages.append(tool_msg)

            log_timeline(f"STEP_{step:02d}_TOOL_RESULTS_ADDED", messages)
            step += 1
            continue

        # KASUS B: Fallback XML/Text Tool Calls (<tool_call>...</tool_call>)
        xml_calls = parse_xml_tool_calls(msg.content or "")
        if xml_calls:
            print(f"    -> AI mengeluarkan {len(xml_calls)} Text/XML Tool Call(s):")
            for idx, xc in enumerate(xml_calls, start=1):
                fn_name = xc["name"]
                fn_args = xc["arguments"]
                fake_id = f"fallback-call-{step}-{idx}"

                print(f"       * Eksekusi Fallback {fn_name}({fn_args})")
                if fn_name in TOOL_REGISTRY:
                    result = TOOL_REGISTRY[fn_name](fn_args)
                else:
                    result = f"Error: Tool '{fn_name}' tidak ditemukan."

                # Masukkan sebagai tool message dengan ID buatan
                tool_msg = {
                    "role": "tool",
                    "tool_call_id": fake_id,
                    "content": str(result)
                }
                messages.append(tool_msg)

            log_timeline(f"STEP_{step:02d}_XML_TOOL_RESULTS_ADDED", messages)
            step += 1
            continue

        # KASUS C: Selesai (Tidak ada pemanggilan tool lagi)
        print("\n" + "=" * 60)
        print("🎉 [JAWABAN AKHIR DARI AGENT]:")
        print("=" * 60)
        print(msg.content)
        print("=" * 60)
        print(f"\n[INFO] Siklus selesai dalam {step} putaran. Detail timeline disimpan di '{LOG_FILE}'.")
        return msg.content

    print(f"\n[WARNING] Batas maksimal putaran ({max_iterations}) tercapai.")
    return None


# ==============================================================================
# 5. ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    prompt_gabungan = (
        "Halo! Tolong cek kondisi cuaca di Jakarta, Bandung, dan Ciamis saat ini. "
        "Selain itu, hari ini saya merasa lelah sekali karena melakukan 10 kali small talk dengan orang baru "
        "dan ada meeting kerja selama 5 jam. Berapa sisa energi sosial saya dan berapa lama saya harus istirahat?"
    )

    run_agent_loop(prompt_gabungan)
