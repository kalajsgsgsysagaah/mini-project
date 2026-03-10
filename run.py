"""
run.py — Launch both FastAPI Backend and React Frontend.
"""

import subprocess
import sys
import os
import threading
import time

ROOT = os.path.dirname(os.path.abspath(__file__))

def run_backend():
    print("🚀  Starting FastAPI Backend...")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "src.api:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=ROOT,
    )

def run_frontend():
    print("🚀  Starting React Frontend (Vite)...")
    # Ensure dependencies are installed if node_modules is missing
    frontend_dir = os.path.join(ROOT, "frontend")
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print("📦  Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, shell=True)
    
    subprocess.run(["npm", "run", "dev"], cwd=frontend_dir, shell=True)

if __name__ == "__main__":
    print("=" * 60)
    print("🌊  Groundwater ML — Local Launch")
    print("    Backend  →  http://localhost:8000")
    print("    Frontend →  http://localhost:5173")
    print("=" * 60)

    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()

    time.sleep(2) # Allow backend to initialize
    run_frontend()
