"""
AI Business Management — Unified Startup Script
Launches both the FastAPI backend and Next.js frontend concurrently.

Usage:
    python start.py
    python start.py --backend-only
    python start.py --frontend-only
"""

import subprocess
import sys
import os
import signal
import time
import threading
import webbrowser
import argparse

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "nexus-analytics")

# ── Config ───────────────────────────────────────────────────────────────────
BACKEND_PORT = 8000
FRONTEND_PORT = 5173
APP_URL = f"http://localhost:{FRONTEND_PORT}"

processes: list[subprocess.Popen] = []
shutting_down = False


def log(prefix: str, line: str, color: str = ""):
    """Print a prefixed log line."""
    reset = "\033[0m"
    print(f"{color}[{prefix}]{reset} {line}", flush=True)


def stream_output(proc: subprocess.Popen, prefix: str, color: str):
    """Read stdout/stderr from a process and print with a prefix."""
    try:
        for raw_line in iter(proc.stdout.readline, b""):
            line = raw_line.decode("utf-8", errors="replace").rstrip()
            if line:
                log(prefix, line, color)
    except (ValueError, OSError):
        pass


def start_backend() -> subprocess.Popen:
    """Start the FastAPI backend with uvicorn."""
    log("SYSTEM", f"Starting FastAPI backend on port {BACKEND_PORT}...", "\033[36m")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app",
         "--host", "127.0.0.1", "--port", str(BACKEND_PORT),
         "--reload"],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )
    processes.append(proc)
    t = threading.Thread(target=stream_output, args=(proc, "BACKEND", "\033[33m"), daemon=True)
    t.start()
    return proc


def start_frontend() -> subprocess.Popen:
    """Start the Vite frontend dev server."""
    log("SYSTEM", f"Starting Vite frontend on port {FRONTEND_PORT}...", "\033[36m")
    proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )
    processes.append(proc)
    t = threading.Thread(target=stream_output, args=(proc, "FRONTEND", "\033[35m"), daemon=True)
    t.start()
    return proc


def open_browser():
    """Open the app in the browser after a short delay."""
    time.sleep(4)
    log("SYSTEM", f"Opening browser at {APP_URL}", "\033[36m")
    webbrowser.open(APP_URL)


def shutdown(*_):
    """Gracefully terminate all child processes."""
    global shutting_down
    if shutting_down:
        return
    shutting_down = True

    log("SYSTEM", "Shutting down all services...", "\033[31m")
    for proc in processes:
        try:
            if os.name == "nt":
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                proc.terminate()
        except (ProcessLookupError, OSError):
            pass

    # Give processes a moment, then force kill
    time.sleep(2)
    for proc in processes:
        try:
            proc.kill()
        except (ProcessLookupError, OSError):
            pass

    log("SYSTEM", "All services stopped.", "\033[31m")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="AI Business Management — Unified Launcher")
    parser.add_argument("--backend-only", action="store_true", help="Start only the backend")
    parser.add_argument("--frontend-only", action="store_true", help="Start only the frontend")
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    args = parser.parse_args()

    # Register signal handlers
    signal.signal(signal.SIGINT, shutdown)
    if os.name == "nt":
        signal.signal(signal.SIGBREAK, shutdown)
    else:
        signal.signal(signal.SIGTERM, shutdown)

    print()
    print("\033[1m==========================================================\033[0m")
    print("\033[1m     AI Business Management & Analytics Suite       \033[0m")
    print("\033[1m==========================================================\033[0m")
    print()

    # Start services
    if not args.frontend_only:
        start_backend()
        time.sleep(2)  # Let backend initialize before frontend

    if not args.backend_only:
        start_frontend()

    # Open browser
    if not args.no_browser and not args.backend_only:
        threading.Thread(target=open_browser, daemon=True).start()

    url_msg = APP_URL if not args.backend_only else f"http://localhost:{BACKEND_PORT}/docs"
    log("SYSTEM", f"Application running at: {url_msg}", "\033[32m")
    log("SYSTEM", "Press Ctrl+C to stop all services\n", "\033[36m")

    # Keep main thread alive
    try:
        while True:
            # Check if any process died
            for proc in processes:
                if proc.poll() is not None:
                    log("SYSTEM", f"A process exited (code {proc.returncode})", "\033[31m")
                    shutdown()
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
