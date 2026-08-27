import os
import sys
import subprocess
import time

def main():
    print("=" * 60)
    print("Q-TRANSPLANT — Intelligent Organ Matching Platform Launcher")
    print("=" * 60)

    # 1. Run tests first
    print("\n[1/3] Running System Verification Tests...")
    res = subprocess.run(["./venv/bin/python3", "test_system.py"])
    if res.returncode != 0:
        print("❌ System tests failed. Aborting startup.")
        sys.exit(1)

    # 2. Start FastAPI Backend
    print("\n[2/3] Starting FastAPI Backend on http://localhost:8000 ...")
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "backend")))
    
    backend_cmd = ["./venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    backend_proc = subprocess.Popen(backend_cmd)

    # 3. Start Frontend HTTP Server
    print("\n[3/3] Starting Frontend HTTP Server on http://localhost:5173 ...")
    frontend_cmd = ["./venv/bin/python3", "-m", "http.server", "5173"]
    frontend_proc = subprocess.Popen(frontend_cmd)

    print("\n" + "=" * 60)
    print("🚀 Q-TRANSPLANT IS LIVE!")
    print("Landing Page: http://localhost:5173/index.html")
    print("Application:  http://localhost:5173/app.html")
    print("FastAPI Docs: http://localhost:8000/docs")
    print("=" * 60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Q-Transplant servers...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    main()
