# Rangkuman Materi Pembelajaran AI Agent & Riset ReAct
**Sumber:** Diskusi Thread [`do you have tools to understand pdf paper?`](file:///C:/Users/ADVAN/PyCharmMiscProject/react_agent_study)  
**Tujuan Pembelajaran:** Memahami fondasi kerja AI Agent modern dari tingkat konsep teoretis, implementasi kode *from scratch*, hingga arsitektur *Native Tool Calling*.

---

## 1. Fondasi Teoretis: Paper ReAct (ICLR 2023)

### A. Identitas Paper Riset
* **Judul:** *ReAct: Synergizing Reasoning and Acting in Language Models*
* **Penulis:** Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao (Princeton University & Google Brain)
* **Publikasi:** ICLR 2023
* **Paper Abstract:** [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)
* **PDF Lengkap:** [arXiv:2210.03629 PDF](https://arxiv.org/pdf/2210.03629.pdf)
* **Website Resmi & Trajectory Visual:** [https://react-lm.github.io/](https://react-lm.github.io/)
* **Repositori Resmi GitHub:** [https://github.com/ysymyx/ReAct](https://github.com/ysymyx/ReAct)
* **Google Research Blog:** [Google Research Blog: ReAct](https://research.google/blog/react-synergizing-reasoning-and-acting-in-language-models/)

### B. Masalah Utama Sebelum ReAct
Sebelum adanya ReAct, pengembangan LLM terbelah menjadi dua pendekatan dengan kelemahan masing-masing:
1. **Reasoning Only (Hanya Bernalar — misal *Chain-of-Thought / CoT*):**
   * Model hanya mengandalkan ingatan bobot internalnya (*internal parametric memory*).
   * **Kelemahan:** Rawan berhalusinasi ketika data tidak ada/usang, serta terjadi *error propagation* (kesalahan awal merembet ke seluruh kesimpulan berikutnya).
2. **Acting Only (Hanya Bertindak):**
   * Model langsung memanggil API atau memilih aksi tanpa fase bernalar.
   * **Kelemahan:** Model kehilangan kemampuan menyusun strategi, tidak bisa mengevaluasi apakah aksi sebelumnya berhasil atau gagal, dan mudah terjebak dalam *infinite loop*.

### C. Solusi ReAct (Reasoning + Acting)
ReAct menggabungkan penalaran (*Reasoning*) dan tindakan (*Acting*) secara berselang-seling (*interleaved*):
$$\text{Berpikir (Thought)} \longrightarrow \text{Bertindak (Action)} \longrightarrow \text{Mengamati (Observation)} \longrightarrow \text{Evaluasi/Berpikir Ulang}$$

```text
[User Task]
    │
    ▼
Thought 1: Menganalisis kebutuhan data atau langkah berikutnya.
Action 1: nama_tool[parameter]
    │  (Eksekusi Python/API nyata)
    ▼
Observation 1: Hasil faktual dari lingkungan / API.
    │
    ▼
Thought 2: Mengevaluasi Observation 1 dan merencanakan langkah selanjutnya.
Action 2: finish[Jawaban final terverifikasi]
```

### D. Mengapa ReAct Menjadi Standar Industri?
* **Thought (Scratchpad):** Berfungsi sebagai ruang kerja dinamis LLM untuk melacak rencana, mendeteksi kegagalan, dan memecah masalah besar menjadi sub-tugas terukur.
* **Observation (Reality Grounding):** Mengikat model ke kenyataan luar, secara drastis menekan angka halusinasi pada benchmark tanya-jawab (HotpotQA, FEVER).
* **Few-shot Prompting:** Mampu mengalahkan model berbasis *Reinforcement Learning* pada lingkungan interaktif (WebShop, ALFWorld) hanya dengan beberapa contoh teks prompt tanpa perlu fine-tuning bobot model.
* **Transparansi & Debuggability:** Developer dapat membaca alur pikir model (`Thought`) dalam bahasa manusia untuk melihat di mana letak kesalahan langkah.

---

## 2. Kumpulan Referensi Riset & Sumber Resmi (Research Links)

### A. Literatur Fondasi AI Agent & Tool Calling
* **Anthropic Research:** [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — Panduan arsitektur agen praktis (Routing, Orchestrator-Workers, Evaluator-Optimizer).
* **Anthropic Cookbook:** [Tool Use & Agent Patterns](https://github.com/anthropics/anthropic-cookbook/tree/main/tool_use) — Contoh implementasi *tool use* dengan Claude SDK.
* **Claude Agent SDK Quickstart:** [Claude Code Agent SDK Documentation](https://code.claude.com/docs/id/agent-sdk/quickstart).
* **OpenAI Platform Guide:** [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling) — Dokumentasi resmi skema JSON tool calling.
* **OpenAI Cookbook:** [How to call functions with chat models](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_call_functions_with_chat_models.ipynb).
* **OpenAI Cookbook Recipes:** [Streaming completions](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_stream_completions.ipynb) & [Handling Rate Limits](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb).
* **OpenRouter Documentation:** [OpenRouter Quick Start Guide](https://openrouter.ai/docs/quick-start) — Panduan integrasi berbagai model gratis/berbayar dengan OpenAI SDK.
* **OpenAI Python SDK Repository:** [openai-python on GitHub](https://github.com/openai/openai-python).

---

## 3. Poin-Poin Teknis & Pelajaran Penting dari Diskusi

### 1. Rahasia *Stop Sequence* pada Prompt-Based ReAct
* Agar LLM tidak memalsukan atau mengarang sendiri hasil output fungsi, kita menetapkan **Stop Token / Stop Sequence** pada string `\nObservation:`.
* Ketika LLM selesai membuat `Action: ...` dan hendak mengetik `Observation:`, API otomatis berhenti memancarkan token. Kontrol berpindah ke script Python kita untuk mengeksekusi tool asli dan menyuntikkan hasil nyata kembali ke riwayat pesan.

### 2. Peran Modul Standar Python `re` & String Parsing
* Modul `re` (*Regular Expressions*) adalah library bawaan resmi Python.
* Pola regex `r"Action:\s*([a-zA-Z0-9_]+)\[(.*?)\]"` digunakan untuk membedah teks bebas LLM menjadi dua komponen:
  * `match.group(1)` $\rightarrow$ Nama fungsi yang dipanggil.
  * `match.group(2)` $\rightarrow$ Argumen parameter fungsi.
* Objek `re.Match`: Menandakan pencocokan berhasil (`None` jika format tidak sesuai pola).
* Fungsi `.strip()`: Wajib digunakan untuk membersihkan karakter spasi, tab (`\t`), dan newline (`\n`) berlebih dari teks LLM agar logika `if response == ...` dan pencocokan teks tidak gagal.

### 3. Analogi Lingkungan Game (Tic-Tac-Toe, Catur, dll.)
* Bagi LLM, **tidak ada perbedaan mekanis** antara mencari informasi di Wikipedia, mengeksekusi query database SQL, atau bermain game seperti Tic-Tac-Toe.
* Semua peran tersebut diperlakukan sebagai **lingkungan interaktif (*environment*)**:
  * Input papan $\rightarrow$ *Observation*
  * Rencana langkah $\rightarrow$ *Thought*
  * Langkah bidak $\rightarrow$ *Action*
* **Self-Correction:** Jika LLM melangkah ke kotak yang sudah terisi, kode engine mengembalikan error di `Observation`, lalu LLM mengevaluasi di `Thought` berikutnya untuk memilih langkah alternatif.

### 4. Integrasi OpenRouter & Penanganan Model Penalaran
* OpenRouter sepenuhnya kompatibel dengan OpenAI Python SDK melalui konfigurasi `base_url="https://openrouter.ai/api/v1"`.
* Model gratis yang mendukung penalaran seperti `nvidia/nemotron-3.5-super-vl:free` dapat diaktifkan menggunakan parameter `extra_body={"reasoning": {"enabled": True}}`.
* **Pencegahan Bug Pydantic Validation:** Saat meneruskan riwayat percakapan (`messages`), jangan mem-pass `reasoning_details` jika bernilai `None` atau tidak didukung oleh validator Pydantic SDK OpenAI terbaru.

### 5. Native Tool Calling vs Prompt-Based ReAct
* **Prompt-Based ReAct:** Menggunakan prompt teks bebas (`Thought / Action / Observation`) dan regex parsing. Fleksibel untuk model apapun, namun rentan kesalahan format string.
* **Native Tool Calling:** Format resmi API di mana tools didefinisikan via JSON Schema (`tools=[{"type": "function", ...}]`). Model yang dilatih (*fine-tuned for tool use*) mengembalikan objek terstruktur `message.tool_calls` dengan properti `id`, `name`, dan `arguments` (JSON).

### 6. Timeline Logging & Observability
* Dalam mengembangkan agent, menyimpan seluruh jejak pesan (`conversation_timeline.json`) sangat esensial untuk memeriksa status `messages_state`, `tool_call_id`, `role: "tool"`, dan respon JSON dari model secara transparan.

---

## 4. Daftar Skrip Python di Folder Ini

Semua skrip pembelajaran dari thread telah disalin ke folder ini:

1. [`react_agent_from_scratch.py`](file:///C:/Users/ADVAN/PyCharmMiscProject/react_agent_study/react_agent_from_scratch.py)
   * **Deskripsi:** Implementasi murni ReAct loop tanpa framework pihak ketiga. Dilengkapi simulasi dummy offline (knowledge base + kalkulator) dan kelas `OpenAILLM` untuk pengujian dengan model nyata.
   * **Cara Menjalankan:**
     ```powershell
     python react_agent_from_scratch.py
     ```

2. [`tictactoe_agent.py`](file:///C:/Users/ADVAN/PyCharmMiscProject/react_agent_study/tictactoe_agent.py)
   * **Deskripsi:** Simulasi interaktif game engine Tic-Tac-Toe yang dimainkan oleh ReAct Agent. Menunjukkan kemampuan deteksi ancaman taktik lawan dan *self-correction* terhadap langkah ilegal.
   * **Cara Menjalankan:**
     ```powershell
     python tictactoe_agent.py
     ```

3. [`agent_with_timeline_logger.py`](file:///C:/Users/ADVAN/PyCharmMiscProject/react_agent_study/agent_with_timeline_logger.py)
   * **Deskripsi:** Script integrasi OpenRouter API yang mengimplementasikan pencatatan snapshot riwayat percakapan secara bertahap ke file JSON (`conversation_timeline.json`).
   * **Cara Menjalankan:**
     ```powershell
     python agent_with_timeline_logger.py
     ```

4. [`native_agent_test.py`](file:///C:/Users/ADVAN/PyCharmMiscProject/react_agent_study/native_agent_test.py)
   * **Deskripsi:** Implementasi *Native Tool Calling* menggunakan skema Function Calling resmi OpenAI API (OpenRouter) dengan fungsi tools cuaca (`get_weather`) dan verifikasi `finish_reason: "tool_calls"`.
   * **Cara Menjalankan:**
     ```powershell
     python native_agent_test.py
     ```

---
*Dokumen ini dibuat otomatis sebagai rangkuman komprehensif materi studi AI Agent dari thread referensi.*
