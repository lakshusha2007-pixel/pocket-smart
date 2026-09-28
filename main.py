import os
import sys

# Ensure backend directory is in python search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(CURRENT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from backend.main import app

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get(
        "HOST",
        "0.0.0.0" if (os.environ.get("RENDER") or (os.environ.get("PORT") and not os.name == "nt")) else "127.0.0.1"
    )

    print("\n=======================================================")
    print("  PocketSmart is running with Firebase Firestore!")
    print(f"  Open in browser: http://127.0.0.1:{port} or http://localhost:{port}")
    print("=======================================================\n")

    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
