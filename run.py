"""
run.py — Start both FastAPI (port 8000) and Gradio (port 7866) together.
Usage:  python run.py
"""

import subprocess
import sys
import os
import threading
import time

ROOT = os.path.dirname(os.path.abspath(__file__))

def run_api():
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "src.api:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=ROOT,
    )

def run_gradio():
    time.sleep(2)  # Let FastAPI start first
    subprocess.run(
        [sys.executable, "src/app.py"],
        cwd=ROOT,
    )

if __name__ == "__main__":
    print("=" * 60)
    print("🚀  Groundwater ML — Launching Services")
    print("    FastAPI  →  http://localhost:8000")
    print("    API Docs →  http://localhost:8000/docs")
    print("    Gradio   →  http://localhost:7866")
    print("=" * 60)

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    run_gradio()
