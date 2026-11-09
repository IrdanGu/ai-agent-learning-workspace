# PyCharm AI & Python Learning Workspace

Repositori ini adalah lingkungan belajar dan eksperimen modular yang mencakup pengembangan **AI Agents**, integrasi **Multi-Provider LLM**, **Computer Vision**, **Data Science & Machine Learning**, serta latihan dasar **Python Programming**.

---

## 📁 Struktur Direktori Proyek

```text
PyCharmMiscProject/
├── agents/                       # Implementasi dan eksperimen AI Agent
│   ├── novita_code_interpreter_agent.py # Autonomous Code Interpreter di Novita Cloud Sandbox
│   ├── agent_workflow_loop.py          # Siklus agen otonom (multi-turn tool calling & timeline logger)
│   ├── react_agent_from_scratch.py     # ReAct agent murni (Reasoning + Acting) tanpa framework
│   ├── calculator_depresi.py           # Tool diagnosis energi baterai sosial & durasi me-time
│   ├── tictactoe_game_agent.py         # Agent interaktif bermain Tic-Tac-Toe dengan self-correction
│   ├── agent_timeline_logger.py        # Logging alur percakapan & tool execution ke JSON
│   ├── native_tool_calling_agent.py    # Native Tool Calling menggunakan OpenAI Function Calling
│   ├── regex_action_parser.py          # Parser regex untuk Action & Argumen dari output model
│   └── RANGKUMAN_MATERI_DAN_RISET_REACT_AGENT.md # Catatan komprehensif teori ReAct & research links
│
├── ai_providers/                 # Integrasi ke berbagai provider LLM & API
│   ├── openrouter_free_chat.py         # Akses model penalaran via OpenRouter (NVIDIA Nemotron free)
│   ├── openai_client_demo.py           # Eksplorasi OpenAI Python SDK (Responses & Completions API)
│   ├── openai_list_models.py           # Script inspeksi daftar model aktif dari OpenAI
│   ├── mistral_chat.py                 # Chat completion menggunakan Mistral AI SDK
│   ├── azure_openai_chat.py            # Integrasi model OpenAI via Azure Endpoint
│   ├── nvidia_nim_glm4_stream.py       # Streaming chat completion via NVIDIA NIM (GLM-4)
│   ├── kimi_moonshot_tester.py         # Pengujian API Moonshot AI (Kimi)
│   └── longcat_tester.py               # Pengujian endpoint model Longcat
│
├── python_basics/                # Algoritma dasar dan manipulasi data Python
│   ├── palindrome_checker.py           # Pengecekan kata palindrom
│   ├── string_title_formatter.py       # Format kapitalisasi dan navigasi index string
│   ├── alphabet_rangoli.py             # Pola cetak alfabet rangoli simetris
│   └── hello_world.py                  # Script pengujian awal lingkungan
│
├── computer_vision/              # Eksperimen pemrosesan gambar & visual AI
│   ├── azure_vision_analyzer.py        # Analisis gambar dari URL menggunakan Azure Computer Vision
│   └── gradient_image_generator.py     # Generator gambar gradien warna sintetis
│
├── data_analysis/                # Analisis data, eksplorasi data, dan machine learning
│   ├── datasets/
│   │   └── all_months_clean.csv        # Dataset tabular bersih untuk analisis tren
│   ├── iris_flower_classification.ipynb# Notebook klasifikasi bunga Iris (Scikit-Learn)
│   ├── exploratory_notebook.ipynb      # Notebook eksperimen dan eksplorasi data
│   └── numpy_linear_layer.py           # Implementasi manual linear layer neural network dengan NumPy
│
├── tests/                        # Automated unit tests
│   └── test_openrouter_free.py         # Unit test untuk OpenRouter integration dengan mock response
│
├── logs/                         # File output JSON, log eksekusi, dan timeline
├── .env                          # Konfigurasi API keys (ignored by git)
└── .gitignore                    # Pengabaian file temporary, virtualenv, dan logs
```

---

## 🚀 Panduan Memulai (Setup & Quickstart)

### 1. Menyiapkan Virtual Environment
Gunakan virtual environment yang sudah ada atau buat baru:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Konfigurasi Environment Variables (`.env`)
Buat atau perbarui file `.env` di root direktori proyek:
```env
OPENROUTER_API_KEY=your_openrouter_key
MISTRAL_API_KEY=your_mistral_key
OPENAI_API_KEY=your_openai_key
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

---

## 📖 Ringkasan Modul & Cara Menjalankan

### 🤖 1. Agents (`agents/`)
Fokus pada pemahaman mekanisme inti AI Agent:
* **Novita Cloud Code Interpreter Agent:**
  ```powershell
  python agents/novita_code_interpreter_agent.py
  ```
* **Autonomous Agent Loop (Multi-Turn Tool Calling):**
  ```powershell
  python agents/agent_workflow_loop.py
  ```
* **ReAct Agent from Scratch:**
  ```powershell
  python agents/react_agent_from_scratch.py
  ```
* **Tic-Tac-Toe Game Agent:**
  ```powershell
  python agents/tictactoe_game_agent.py
  ```
* **Native Tool Calling:**
  ```powershell
  python agents/native_tool_calling_agent.py
  ```
* **Catatan Riset ReAct:** Buka dokumen [`agents/RANGKUMAN_MATERI_DAN_RISET_REACT_AGENT.md`](agents/RANGKUMAN_MATERI_DAN_RISET_REACT_AGENT.md) untuk mempelajari teori paper ReAct (arXiv:2210.03629), perbandingan CoT vs ReAct, dan referensi resmi Anthropic & OpenAI.

---

### 🌐 2. AI Providers (`ai_providers/`)
Contoh kode modular untuk berinteraksi dengan berbagai ekosistem model AI:
* **OpenRouter Free Model:**
  ```powershell
  python ai_providers/openrouter_free_chat.py
  ```
* **Mistral AI:**
  ```powershell
  python ai_providers/mistral_chat.py
  ```
* **NVIDIA NIM Streaming:**
  ```powershell
  python ai_providers/nvidia_nim_glm4_stream.py
  ```

---

### 🐍 3. Python Basics (`python_basics/`)
Latihan dasar logika pemrograman dan manipulasi struktur data Python:
* **Cek Palindrom:**
  ```powershell
  python python_basics/palindrome_checker.py
  ```
* **Alphabet Rangoli:**
  ```powershell
  python python_basics/alphabet_rangoli.py
  ```

---

### 👁️ 4. Computer Vision (`computer_vision/`)
* **Analisis Gambar Azure Vision:**
  ```powershell
  python computer_vision/azure_vision_analyzer.py
  ```
* **Buat Gambar Gradien:**
  ```powershell
  python computer_vision/gradient_image_generator.py
  ```

---

### 📊 5. Data Analysis (`data_analysis/`)
* **NumPy Neural Network Layer:**
  ```powershell
  python data_analysis/numpy_linear_layer.py
  ```
* **Jupyter Notebooks:** Jalankan Jupyter Lab / Notebook atau buka melalui PyCharm untuk menjalankan:
  - `data_analysis/iris_flower_classification.ipynb`
  - `data_analysis/exploratory_notebook.ipynb`

---

### 🧪 6. Testing (`tests/`)
Jalankan unit test otomatis menggunakan `unittest`:
```powershell
python -m unittest discover tests/
```
