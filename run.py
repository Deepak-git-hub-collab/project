"""
ShieldPlus AI - Launcher Script
Boots the FastAPI backend server, auto-starts the real-time transaction simulator,
and launches the browser command center.
"""

import sys
import time
import socket
import webbrowser
import threading
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from backend.app.core.config import settings

def find_available_port(host: str, preferred_port: int, max_trials: int = 10) -> int:
    """Finds an available TCP port starting from preferred_port."""
    for port in range(preferred_port, preferred_port + max_trials):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
                try:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
                except Exception:
                    pass
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    return preferred_port

def open_browser(url: str):
    time.sleep(1.2)
    print(f"\n[ShieldPlus AI] Launching Command Center UI at: {url}\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass

if __name__ == "__main__":
    active_port = find_available_port(settings.HOST, settings.PORT)
    if active_port != settings.PORT:
        print(f"[!] Warning: Port {settings.PORT} is already in use. Auto-switching to port {active_port}.")
        settings.PORT = active_port

    target_url = f"http://{settings.HOST}:{active_port}"

    print("=" * 70)
    print("   SHIELDPLUS AI — REAL-TIME FINANCIAL FRAUD & ANOMALY ENGINE")
    print("=" * 70)
    print(f"[*] Core Engine: FastAPI + WebSockets + Scikit-Learn Isolation Forest")
    print(f"[*] Database: SQLite ({settings.DB_PATH})")
    print(f"[*] Host: {target_url}")
    print(f"[*] Documentation: {target_url}/docs")
    print("=" * 70)

    # Launch browser in separate background thread
    threading.Thread(target=open_browser, args=(target_url,), daemon=True).start()

    # Run Uvicorn server with graceful interruption
    try:
        uvicorn.run(
            "backend.app.main:app",
            host=settings.HOST,
            port=active_port,
            reload=settings.DEBUG,
            reload_dirs=[str(ROOT_DIR / "backend")],
            reload_excludes=["*.db", "*.db-journal", "*.db-wal", "*.log"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n[ShieldPlus AI] Service shut down successfully.")
    except OSError as err:
        print(f"\n[ShieldPlus AI] Network error binding to port {active_port}: {err}")
        print("[ShieldPlus AI] If another server process is already running, please stop it or run start.ps1 again.")
