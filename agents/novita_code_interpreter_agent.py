"""
Autonomous Code Interpreter Agent with Novita Cloud Sandbox
============================================================
Arsitektur:
- OTAK (Brain): Model LLM (via OpenRouter Free API atau model lainnya)
- TANGAN (Hands): Novita Cloud Sandbox (MicroVM Linux terisolasi menggunakan kredit $100 Anda)

Fitur:
1. Menjalankan Python & Bash di cloud tanpa risiko merusak OS lokal.
2. Otomatis menangkap output print, error traceback, dan gambar plot (matplotlib/seaborn).
3. Pengelolaan lifecycle otomatis (auto kill/pause) agar hemat kuota per-detik dan kredit tidak bocor.
4. Fallback simulation mode jika NOVITA_API_KEY belum dimasukkan ke file .env.
"""

import os
import sys
import json
import base64
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# Pastikan konsol Windows UTF-8 aman
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
NOVITA_API_KEY = os.getenv("NOVITA_API_KEY")

ai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Direktori lokal untuk menyimpan artefak hasil unduhan dari cloud (misal grafik plot)
OUTPUT_DIR = "data_analysis/sandbox_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==============================================================================
# 1. PENGELOLA NOVITA CLOUD SANDBOX (MicroVM Manager)
# ==============================================================================

class CloudSandboxRunner:
    """Mengelola siklus hidup MicroVM Novita Cloud Sandbox."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NOVITA_API_KEY")
        self.sandbox = None
        self._is_mock = not bool(self.api_key)

    def start(self):
        """Membuat instance Sandbox baru di cloud."""
        if self._is_mock:
            print("[INFO] NOVITA_API_KEY belum terdeteksi di .env. Menggunakan Mode Simulasi Lokal.")
            return True

        try:
            from novita_sandbox import CodeInterpreterSandbox
            print("[CLOUD] Menghubungi Novita API untuk membuat MicroVM Sandbox...")
            # Buat sandbox dengan timeout keamanan 10 menit (agar kredit tidak terkuras jika lupa di-kill)
            self.sandbox = CodeInterpreterSandbox.create(timeout=600)
            print(f"[CLOUD] Sandbox aktif! ID: {self.sandbox.sandbox_id}")
            return True
        except Exception as e:
            print(f"[WARNING] Gagal membuat Sandbox di cloud: {e}")
            print("[INFO] Beralih otomatis ke Mode Simulasi.")
            self._is_mock = True
            return True

    def execute_python(self, code: str) -> Dict[str, Any]:
        """Mengeksekusi kode Python di dalam Cloud Sandbox."""
        if self._is_mock:
            return self._mock_execute_python(code)

        try:
            print(f"\n[CLOUD] Mengirim kode Python ke Sandbox ({len(code)} karakter)...")
            execution = self.sandbox.run_code(code)

            stdout_logs = execution.logs.stdout if execution.logs else []
            stderr_logs = execution.logs.stderr if execution.logs else []
            log_text = "\n".join(stdout_logs) if stdout_logs else ""
            err_text = "\n".join(stderr_logs) if stderr_logs else ""

            saved_images = []
            if execution.results:
                for idx, res in enumerate(execution.results):
                    # Jika ada output gambar (misal dari plt.show() matplotlib)
                    if hasattr(res, "png") and res.png:
                        img_path = os.path.join(OUTPUT_DIR, f"chart_{idx + 1}.png")
                        with open(img_path, "wb") as f:
                            f.write(base64.b64decode(res.png))
                        saved_images.append(img_path)

            error_info = str(execution.error) if execution.error else ""

            result_summary = ""
            if log_text:
                result_summary += f"Output:\n{log_text}\n"
            if err_text:
                result_summary += f"Errors/Warnings:\n{err_text}\n"
            if error_info:
                result_summary += f"Execution Error:\n{error_info}\n"
            if saved_images:
                result_summary += f"Visual Charts Tersimpan di Lokal: {saved_images}\n"

            return {
                "success": not bool(execution.error),
                "summary": result_summary or "Kode berhasil dieksekusi tanpa output teks.",
                "charts": saved_images
            }
        except Exception as e:
            return {"success": False, "summary": f"Gagal mengeksekusi di cloud sandbox: {e}", "charts": []}

    def execute_shell(self, command: str) -> Dict[str, Any]:
        """Mengeksekusi perintah terminal Bash di dalam Cloud Sandbox."""
        if self._is_mock:
            return {"success": True, "summary": f"[SIMULASI] Menjalankan bash: {command}"}

        try:
            print(f"\n[CLOUD] Menjalankan perintah terminal: {command}")
            result = self.sandbox.commands.run(command)
            output = f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            return {"success": result.exit_code == 0, "summary": output}
        except Exception as e:
            return {"success": False, "summary": f"Error terminal: {e}"}

    def close(self):
        """Mematikan sandbox untuk menghentikan pemotongan biaya kredit per detik."""
        if self.sandbox:
            try:
                print(f"[CLOUD] Mematikan Sandbox ID: {self.sandbox.sandbox_id}...")
                self.sandbox.kill()
                print("[CLOUD] Sandbox berhasil dimatikan. Billing komputasi berhenti.")
            except Exception as e:
                print(f"[WARNING] Gagal mematikan sandbox: {e}")
            self.sandbox = None

    def _mock_execute_python(self, code: str) -> Dict[str, Any]:
        """Simulasi lokal sederhana saat API key belum dipasang."""
        import io
        from contextlib import redirect_stdout, redirect_stderr
        f_out = io.StringIO()
        f_err = io.StringIO()
        success = True
        try:
            with redirect_stdout(f_out), redirect_stderr(f_err):
                # Eksekusi lokal terbatas
                exec(code, {"__name__": "__main__"})
        except Exception as e:
            success = False
            f_err.write(str(e))
        return {
            "success": success,
            "summary": f"[MODE SIMULASI LOKAL]\nOutput:\n{f_out.getvalue()}\nErrors:\n{f_err.getvalue()}",
            "charts": []
        }


# ==============================================================================
# 2. DEFINISI TOOLS UNTUK LLM
# ==============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_python_in_cloud_sandbox",
            "description": (
                "Mengeksekusi kode Python di dalam Cloud Sandbox Linux (Novita). "
                "Lingkungan ini memiliki Python, NumPy, Pandas, Matplotlib, Scipy, dan akses internet. "
                "Gunakan untuk komputasi matematika, pemrosesan data, pembuatan grafik, atau algoritma rumit."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Kode Python lengkap yang ingin dieksekusi. Gunakan print() untuk melihat hasil."
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_bash_command_in_cloud_sandbox",
            "description": "Menjalankan perintah terminal Linux di dalam cloud sandbox (misal: pip install <package>, ls, curl).",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Perintah bash yang ingin dijalankan di sandbox."
                    }
                },
                "required": ["command"]
            }
        }
    }
]


# ==============================================================================
# 3. AUTONOMOUS CODE INTERPRETER AGENT LOOP
# ==============================================================================

def run_code_interpreter_agent(user_request: str, max_turns: int = 6):
    """
    Menjalankan Agent yang menganalisis tugas, menulis kode, mengeksekusi di Cloud Sandbox,
    dan menyusun laporan hasil analisis akhir.
    """
    print("\n" + "=" * 65)
    print("🚀 MEMULAI AUTONOMOUS CODE INTERPRETER AGENT (NOVITA SANDBOX)")
    print("=" * 65)
    print(f"Permintaan Pengguna: \"{user_request}\"\n")

    sandbox_runner = CloudSandboxRunner()
    sandbox_runner.start()

    messages = [
        {
            "role": "system",
            "content": (
                "Kamu adalah AI Data Scientist dan Senior Python Engineer yang handal. "
                "Kamu memiliki akses langsung ke 'execute_python_in_cloud_sandbox' dan 'run_bash_command_in_cloud_sandbox'. "
                "Ketika pengguna meminta analisis, simulasi, pembuatan grafik, atau kalkulasi numerik, "
                "TULIS KODE PYTHON NYATA dan panggil tool tersebut. "
                "Setelah tool dieksekusi, baca outputnya dan sajikan penjelasan analisis yang mudah dipahami dan profesional."
            )
        },
        {"role": "user", "content": user_request}
    ]

    try:
        step = 1
        while step <= max_turns:
            print(f">>> [Putaran {step}]: Menghubungi LLM untuk merencanakan & menulis kode...")
            response = ai_client.chat.completions.create(
                model="nvidia/nemotron-3.5-super-vl:free",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )

            msg = response.choices[0].message
            messages.append(msg)

            # Jika model meminta pemanggilan tool
            if msg.tool_calls:
                print(f"    -> AI memutuskan memanggil {len(msg.tool_calls)} tool:")
                for tc in msg.tool_calls:
                    fn_name = tc.function.name
                    try:
                        fn_args = json.loads(tc.function.arguments)
                    except Exception:
                        fn_args = {}

                    if fn_name == "execute_python_in_cloud_sandbox":
                        code = fn_args.get("code", "")
                        print(f"       [TOOL CALL] Menjalankan Python Code:")
                        for line in code.strip().split("\n")[:6]:
                            print(f"         | {line}")
                        if len(code.strip().split("\n")) > 6:
                            print("         | ...")

                        res = sandbox_runner.execute_python(code)
                        tool_output = res["summary"]

                    elif fn_name == "run_bash_command_in_cloud_sandbox":
                        cmd = fn_args.get("command", "")
                        print(f"       [TOOL CALL] Menjalankan Shell: {cmd}")
                        res = sandbox_runner.execute_shell(cmd)
                        tool_output = res["summary"]
                    else:
                        tool_output = f"Tool '{fn_name}' tidak dikenal."

                    print(f"       <- Hasil Eksekusi:\n{tool_output[:250]}...")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": tool_output
                    })

                step += 1
                continue

            # Jika sudah tidak ada tool call, artinya AI sudah selesai menyusun jawaban final
            print("\n" + "=" * 65)
            print("✅ JAWABAN AKHIR DARI CODE INTERPRETER AGENT:")
            print("=" * 65)
            print(msg.content)
            print("=" * 65)
            return msg.content

    finally:
        # SELALU pastikan sandbox dimatikan agar kredit $100 tidak terbuang sia-sia
        sandbox_runner.close()


# ==============================================================================
# 4. ENTRY POINT CONTOH
# ==============================================================================

if __name__ == "__main__":
    contoh_tugas = (
        "Hitung nilai faktorial dari 30 dan periksa apakah ada bilangan prima di antara "
        "angka 1.000.000 hingga 1.000.050. Tuliskan kodenya dan jalankan di sandbox."
    )
    run_code_interpreter_agent(contoh_tugas)
