import uvicorn
import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"\n[FormEase Backend] Starting on http://{host}:{port}")
    print(f"[FormEase Docs] Interactive API Docs available at http://{host}:{port}/docs\n")
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)
