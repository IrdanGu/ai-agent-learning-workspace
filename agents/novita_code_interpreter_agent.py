"""
Autonomous Code Interpreter Agent with Novita Cloud Sandbox
============================================================
Mengikuti Best Practice resmi dari 'novita-sandbox-skills' (SDK >= 2.1.0):
1. Client Entry Point terpadu: `from novita_sandbox import Novita`
2. Proteksi Biaya Ganda:
   - Hard Timeout (maksimal durasi sandbox aktif): `timeout=300` detik
   - Idle Timeout (otomatis mati jika tidak ada aktivitas): `metadata={"idle_timeout": "60"}`
   - Lifecycle eksplisit: `lifecycle={"on_timeout": "kill"}`
3. Resource Clean-up: Context Manager (`__enter__` & `__exit__`) untuk menjamin `sandbox.kill()` selalu terpanggil.
4. Per-Command Timeout: Perintah shell dibatasi `timeout=60` detik agar tidak hang.
5. Filesystem API: Mendukung transfer file langsung lewat `sandbox.files`.
6. Fallback Simulation: Aman dijalankan offline jika NOVITA_API_KEY belum dipasang.
"""

import os
import sys
import json
import base64
from typing import Optional, Dict, Any, List
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

# Direktori lokal untuk menyimpan artefak hasil unduhan dari cloud (misal grafik plot / file)
OUTPUT_DIR = "data_analysis/sandbox_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==============================================================================
# 1. PENGELOLA NOVITA CLOUD SANDBOX (Sesuai novita-sandbox-skills Best Practice)
# ==============================================================================

class CloudSandboxRunner:
    """
    Mengelola siklus hidup MicroVM Novita Cloud Sandbox secara aman & hemat biaya.
    Mendukung Context Manager ('with CloudSandboxRunner() as runner:').
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NOVITA_API_KEY")
        self.novita = None
        self.sandbox = None
        self._is_mock = not bool(self.api_key)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def start(self):
        """Membuat instance Sandbox baru di cloud dengan best practice parameter."""
        if self._is_mock:
            print("[INFO] NOVITA_API_KEY belum terdeteksi di .env. Menggunakan Mode Simulasi Lokal.")
            return True

        try:
            # Best Practice 1: Gunakan unified entry point Novita client
            from novita_sandbox import Novita

            self.novita = Novita(api_key=self.api_key)
            print("[CLOUD] Menghubungi Novita API untuk menginisialisasi MicroVM Sandbox...")

            # Best Practice 2: Lindungi kredit dengan timeout, idle_timeout, dan lifecycle kill
            self.sandbox = self.novita.code_interpreter.create(
                timeout=300,  # Hard timeout: 5 menit (cukup untuk task agent)
                metadata={"idle_timeout": "60"},  # Auto-kill jika nganggur 60 detik
                lifecycle={"on_timeout": "kill"}   # Matikan penuh saat timeout tercapai
            )
            print(f"[CLOUD] Sandbox aktif & terisolasi! ID: {self.sandbox.sandbox_id}")
            return True
        except Exception as e:
            print(f"[WARNING] Gagal membuat Sandbox di cloud: {e}")
            print("[INFO] Beralih otomatis ke Mode Simulasi Lokal.")
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
                    # Jika ada output visual grafik (misal plt.show() dari matplotlib/seaborn)
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
                result_summary += f"Warnings/Stderr:\n{err_text}\n"
            if error_info:
                result_summary += f"Execution Error:\n{error_info}\n"
            if saved_images:
                result_summary += f"Visual Charts Berhasil Diunduh: {saved_images}\n"

            return {
                "success": not bool(execution.error),
                "summary": result_summary or "Kode berhasil dieksekusi tanpa error teks.",
                "charts": saved_images
            }
        except Exception as e:
            return {"success": False, "summary": f"Gagal eksekusi sandbox: {e}", "charts": []}

    def execute_shell(self, command: str) -> Dict[str, Any]:
        """Mengeksekusi perintah terminal Bash di dalam Cloud Sandbox dengan per-command timeout."""
        if self._is_mock:
            return {"success": True, "summary": f"[SIMULASI] Menjalankan bash: {command}"}

        try:
            print(f"\n[CLOUD] Menjalankan perintah terminal: {command}")
            # Best Practice 3: Gunakan per-command timeout (60 detik)
            result = self.sandbox.commands.run(command, timeout=60)
            output = f"Exit code: {result.exit_code}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            return {"success": result.exit_code == 0, "summary": output}
        except Exception as e:
            return {"success": False, "summary": f"Error terminal sandbox: {e}"}

    def write_file_to_sandbox(self, path: str, content: str) -> Dict[str, Any]:
        """Menulis file ke sistem file Sandbox menggunakan Filesystem API resmi."""
        if self._is_mock:
            return {"success": True, "summary": f"[SIMULASI] Menulis file ke {path}"}

        try:
            self.sandbox.files.write(path, content)
            return {"success": True, "summary": f"File berhasil ditulis ke sandbox di path: {path}"}
        except Exception as e:
            return {"success": False, "summary": f"Gagal menulis file: {e}"}

    def read_file_from_sandbox(self, path: str) -> Dict[str, Any]:
        """Membaca isi file dari sistem file Sandbox menggunakan Filesystem API resmi."""
        if self._is_mock:
            return {"success": True, "summary": f"[SIMULASI] Isi file dari {path}"}

        try:
            content = self.sandbox.files.read(path)
            return {"success": True, "summary": content}
        except Exception as e:
            return {"success": False, "summary": f"Gagal membaca file: {e}"}

    def close(self):
        """Mematikan sandbox untuk menghentikan billing biaya komputasi per detik."""
        if self.sandbox:
            try:
                print(f"[CLOUD] Mematikan Sandbox ID: {self.sandbox.sandbox_id}...")
                self.sandbox.kill()
                print("[CLOUD] Sandbox berhasil dimatikan (KILLED). Billing komputasi selesai.")
            except Exception as e:
                print(f"[WARNING] Gagal mematikan sandbox: {e}")
            finally:
                self.sandbox = None

    def _mock_execute_python(self, code: str) -> Dict[str, Any]:
        """Simulasi lokal sederhana saat API key belum dipasang di .env."""
        import io
        from contextlib import redirect_stdout, redirect_stderr
        f_out = io.StringIO()
        f_err = io.StringIO()
        success = True
        try:
            with redirect_stdout(f_out), redirect_stderr(f_err):
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
                "Mengeksekusi kode Python di dalam Cloud Sandbox Linux terisolasi (Novita). "
                "Tersedia modul Python lengkap (math, numpy, pandas, matplotlib, scipy). "
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
            "description": "Menjalankan perintah terminal Linux di sandbox (misal: pip install <package>, ls, head).",
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
    dan menyusun laporan hasil analisis akhir secara otonom.
    """
    print("\n" + "=" * 65)
    print("🚀 MEMULAI AUTONOMOUS CODE INTERPRETER AGENT (NOVITA SANDBOX)")
    print("=" * 65)
    print(f"Permintaan Pengguna: \"{user_request}\"\n")

    # Best Practice: Gunakan Context Manager untuk menggaransi sandbox.kill() selalu dieksekusi
    with CloudSandboxRunner() as sandbox_runner:
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


# ==============================================================================
# 4. ENTRY POINT CONTOH
# ==============================================================================

if __name__ == "__main__":
    contoh_tugas = (
        "Hitung nilai faktorial dari 30 dan periksa apakah ada bilangan prima di antara "
        "angka 1.000.000 hingga 1.000.050. Tuliskan kodenya dan jalankan di sandbox."
    )
    run_code_interpreter_agent(contoh_tugas)
