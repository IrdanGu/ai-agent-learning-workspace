"""
ReAct Agent from Scratch (Berdasarkan Paper arXiv:2210.03629)
=============================================================
Skrip ini mengimplementasikan pola ReAct murni tanpa framework (tanpa LangChain/CrewAI).
Dapat dijalankan langsung secara mandiri (standalone simulation) maupun dengan API LLM nyata.

Siklus Inti ReAct:
  Input Pertanyaan
       |
       v
  [1. Thought]     -> Model bernalar tentang apa yang perlu dilakukan
       |
       v
  [2. Action]      -> Model memilih tool dan parameter yang ingin dipanggil
       |
       v
  [3. Observation] -> Lingkungan/Tool dieksekusi, hasilnya diumpankan kembali ke prompt
       |
       +------------> (Ulangi sampai Action: finish[jawaban])
"""

import re
import math

# ==============================================================================
# 1. DEFINISI TOOLS (ALAT YANG BISA DIGUNAKAN AGENT)
# ==============================================================================

def tool_search(query: str) -> str:
    """Simulasi pencarian mini Wikipedia / database fakta."""
    query_clean = query.lower().strip()
    knowledge_base = {
        "joko widodo": "Joko Widodo adalah Presiden ke-7 Indonesia yang menjabat dari 2014 hingga 2024. Lahir di Surakarta pada 21 Juni 1961.",
        "prabowo subianto": "Prabowo Subianto adalah Presiden ke-8 Indonesia yang dilantik pada 20 Oktober 2024. Lahir pada 17 Oktober 1951.",
        "borobudur": "Borobudur adalah candi Buddha terbesar di dunia yang terletak di Magelang, Jawa Tengah, dibangun pada abad ke-8 dan ke-9 Masehi.",
        "monas": "Monumen Nasional (Monas) memiliki tinggi 132 meter (433 kaki) dan terletak di Jakarta Pusat.",
        "gunung everest": "Gunung Everest adalah gunung tertinggi di dunia dengan ketinggian puncak 8.848,86 meter di atas permukaan laut."
    }
    for key, val in knowledge_base.items():
        if key in query_clean:
            return f"Found: {val}"
    return f"No direct match found for '{query}'. Coba kata kunci yang lebih spesifik."

def tool_calculator(expression: str) -> str:
    """Menghitung ekspresi matematika sederhana."""
    try:
        # Sanitasi ekspresi matematika dasar
        clean_expr = re.sub(r'[^0-9\+\-\*\/\(\)\.\s\^]', '', expression).replace('^', '**')
        result = eval(clean_expr, {"__builtins__": None, "math": math})
        return str(result)
    except Exception as e:
        return f"Error kalkulasi: {e}"

def tool_social_battery(param_str: str) -> str:
    """
    Mendiagnosis sisa social battery dan kebutuhan recharge me-time.
    Format argumen (dipisah koma): small_talk, meetings_hours, unexpected_calls, crowd_hours
    Contoh: 5, 2, 1, 3
    """
    try:
        from agents.calculator_depresi import calculator_depresi
    except ImportError:
        from calculator_depresi import calculator_depresi

    parts = [p.strip() for p in param_str.split(",") if p.strip()]
    st = int(parts[0]) if len(parts) > 0 else 0
    meet = int(parts[1]) if len(parts) > 1 else 0
    calls = int(parts[2]) if len(parts) > 2 else 0
    crowd = int(parts[3]) if len(parts) > 3 else 0
    return calculator_depresi(st, meet, calls, crowd)

# Registry tools
TOOLS = {
    "search": tool_search,
    "calculator": tool_calculator,
    "social_battery": tool_social_battery
}

# ==============================================================================
# 2. PROMPT TEMPLATE REACT (Sesuai format asli paper Shunyu Yao et al.)
# ==============================================================================

REACT_SYSTEM_PROMPT = """Selesaikan pertanyaan berikut dengan menggunakan pola Thought, Action, Observation.

Tools yang tersedia:
- search[query]: Mencari informasi faktual dari database pengetahuan.
- calculator[ekspresi]: Menghitung operasi matematika dasar.
- social_battery[small_talk, meetings, calls, crowd]: Menghitung sisa energi sosial & waktu me-time recharging.
- finish[jawaban]: Gunakan ini setelah kamu yakin memiliki jawaban final untuk pengguna.

Format yang HARUS diikuti:
Question: [pertanyaan pengguna]
Thought: [penalaranmu tentang apa langkah yang perlu diambil]
Action: nama_tool[argumen]
Observation: [hasil dari tool akan diberikan di sini]
... (ulangi siklus Thought/Action/Observation jika diperlukan) ...
Thought: [penalaran akhir]
Action: finish[jawaban lengkap]

Contoh Trajectory:
Question: Berapa selisih tinggi Monas dengan puncak Borobudur jika tinggi Borobudur adalah 35 meter?
Thought: Saya perlu mencari tinggi Monas terlebih dahulu.
Action: search[monas]
Observation: Found: Monumen Nasional (Monas) memiliki tinggi 132 meter (433 kaki) dan terletak di Jakarta Pusat.
Thought: Monas tingginya 132 meter dan Borobudur 35 meter. Sekarang saya perlu menghitung 132 - 35.
Action: calculator[132 - 35]
Observation: 97
Thought: Selisih tingginya adalah 97 meter. Saya siap memberikan jawaban akhir.
Action: finish[Selisih tinggi Monas dan Borobudur adalah 97 meter.]
"""

# ==============================================================================
# 3. ENGINE REACT AGENT
# ==============================================================================

class MockLLM:
    """
    Mock LLM untuk demonstrasi offline tanpa API key.
    Menstimulasikan respon cerdas model LLM yang mengikuti format ReAct.
    """
    def __init__(self):
        self.step = 0

    def generate(self, prompt: str) -> str:
        # Simulasi respon model langkah demi langkah untuk pertanyaan Presiden ke-7 & 8
        if "Berapa umur Prabowo Subianto saat dilantik pada tahun 2024?" in prompt:
            if "Observation 1:" not in prompt:
                return (
                    "Thought 1: Saya perlu mencari tahu tanggal lahir Prabowo Subianto dan tahun pelantikannya.\n"
                    "Action 1: search[prabowo subianto]"
                )
            elif "Observation 2:" not in prompt:
                return (
                    "Thought 2: Prabowo Subianto lahir pada 17 Oktober 1951 dan dilantik pada 20 Oktober 2024. "
                    "Saya perlu menghitung umur beliau pada saat pelantikan yaitu tahun 2024 dikurangi 1951.\n"
                    "Action 2: calculator[2024 - 1951]"
                )
            else:
                return (
                    "Thought 3: Hasil perhitungan adalah 73 tahun, dan karena beliau dilantik 20 Oktober (3 hari setelah ulang tahun ke-73 pada 17 Oktober), maka umurnya tepat 73 tahun.\n"
                    "Action 3: finish[Prabowo Subianto berumur 73 tahun saat dilantik menjadi Presiden pada Oktober 2024.]"
                )
        return "Thought: Saya tidak memiliki skenario simulasi untuk pertanyaan ini.\nAction: finish[Mohon gunakan LLM API nyata.]"


def run_react_agent(question: str, llm=None, max_steps: int = 6):
    """
    Eksekusi loop ReAct:
    Loop while:
       Prompt -> LLM -> Parse Thought & Action -> Execute Tool -> Observation -> Repeat
    """
    if llm is None:
        llm = MockLLM()

    print("\n" + "="*70)
    print(f"PERTANYAAN: {question}")
    print("="*70)

    prompt = REACT_SYSTEM_PROMPT + f"\nQuestion: {question}\n"
    
    # Regex untuk mengekstrak Action: tool_name[arguments]
    action_pattern = re.compile(r"Action(?:\s*\d*)?:\s*([a-zA-Z0-9_]+)\[(.*?)\]", re.DOTALL)

    for step in range(1, max_steps + 1):
        print(f"\n--- [LANGKAH KE-{step}] ---")
        
        # 1. Kirim prompt ke LLM
        output = llm.generate(prompt)
        print(output.strip())
        prompt += output.strip() + "\n"

        # 2. Parse Action dari output LLM
        match = action_pattern.search(output)
        if not match:
            print("❌ Error: Format Action tidak valid atau LLM berhenti tanpa aksi.")
            break

        tool_name, tool_arg = match.group(1), match.group(2).strip()

        # 3. Cek apakah agent sudah selesai
        if tool_name == "finish":
            print("\n" + "="*70)
            print(f"[SUCCESS] JAWABAN AKHIR: {tool_arg}")
            print("="*70)
            return tool_arg

        # 4. Eksekusi Tool (Acting)
        if tool_name in TOOLS:
            observation = TOOLS[tool_name](tool_arg)
        else:
            observation = f"Error: Tool '{tool_name}' tidak ditemukan. Pilihan: {list(TOOLS.keys())}"

        # 5. Suntikkan Observation kembali ke konteks prompt
        obs_text = f"Observation {step}: {observation}"
        print(f"--> {obs_text}")
        prompt += f"{obs_text}\n"

    print("\n[WARNING] Agent mencapai batas langkah maksimal tanpa jawaban akhir.")
    return None

class OpenAILLM:
    """
    Klien untuk menghubungkan ReAct agent ke model LLM nyata
    (OpenAI, Ollama, Groq, OpenRouter, atau endpoint OpenAI-compatible lainnya).
    """
    def __init__(self, api_key: str = None, base_url: str = None, model: str = "gpt-4o-mini"):
        import os
        from openai import OpenAI
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY", "your-api-key"),
            base_url=base_url or os.getenv("OPENAI_BASE_URL", None)
        )
        self.model = model

    def generate(self, prompt: str) -> str:
        # Kita set stop token agar LLM berhenti setelah memanggil Action
        # sehingga kontrol kembali ke Python untuk mengeksekusi Tool!
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stop=["\nObservation:", "\nObservation "],
            temperature=0.0
        )
        return response.choices[0].message.content or ""

if __name__ == "__main__":
    import sys
    # Memastikan encoding output aman di konsol Windows
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    pertanyaan = "Berapa umur Prabowo Subianto saat dilantik pada tahun 2024?"
    
    # Menjalankan agent (Default menggunakan MockLLM agar langsung bekerja offline)
    # Untuk memakai model asli, ganti llm=OpenAILLM(api_key="...", model="gpt-4o-mini")
    run_react_agent(pertanyaan, llm=MockLLM())

