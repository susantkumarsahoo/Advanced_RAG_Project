import subprocess
import sys
import time
import signal
import os

# ── Config ────────────────────────────────────────────────────────────────────
FASTAPI_HOST = "127.0.0.1"
FASTAPI_PORT = 8000
STREAMLIT_PORT = 8501

processes = []


def start_fastapi():
    print("🚀 Starting FastAPI backend on http://{}:{}".format(FASTAPI_HOST, FASTAPI_PORT))
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", FASTAPI_HOST,
            "--port", str(FASTAPI_PORT),
            "--reload",
        ],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    return proc


def start_streamlit():
    print("🌐 Starting Streamlit frontend on http://localhost:{}".format(STREAMLIT_PORT))
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run",
            "streamlit_app.py",
            "--server.port", str(STREAMLIT_PORT),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
        ],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    return proc


def shutdown(sig, frame):
    print("\n🛑 Shutting down all services...")
    for proc in processes:
        proc.terminate()
    for proc in processes:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    print("✅ All services stopped.")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown)   # Ctrl+C
    signal.signal(signal.SIGTERM, shutdown)  # kill

    # Start both services
    processes.append(start_fastapi())
    time.sleep(2)                            # give FastAPI a moment to bind
    processes.append(start_streamlit())

    print("\n" + "─" * 50)
    print("  ⚡ RAG Chat is running!")
    print("  Backend  → http://{}:{}".format(FASTAPI_HOST, FASTAPI_PORT))
    print("  Frontend → http://localhost:{}".format(STREAMLIT_PORT))
    print("  Press Ctrl+C to stop everything")
    print("─" * 50 + "\n")

    # Keep alive and watch for unexpected exits
    while True:
        for i, proc in enumerate(processes):
            ret = proc.poll()
            if ret is not None:
                name = "FastAPI" if i == 0 else "Streamlit"
                print(f"⚠️  {name} exited with code {ret}. Shutting down...")
                shutdown(None, None)
        time.sleep(2)
        
        
        
# python run.py