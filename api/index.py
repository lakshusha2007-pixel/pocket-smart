import os
import sys
import traceback

# -------------------------------------------------------------------
# Setup paths for Vercel Serverless environment
# -------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

for directory in (ROOT_DIR, BACKEND_DIR):
    if directory not in sys.path:
        sys.path.insert(0, directory)

# Mark environment as Vercel if running in Vercel lambda
if "VERCEL" not in os.environ:
    os.environ["VERCEL"] = "1"

# -------------------------------------------------------------------
# Import FastAPI application
# -------------------------------------------------------------------
try:
    from backend.main import app
except Exception as exc:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    err_trace = traceback.format_exc()
    print("FATAL: Failed to import backend.main:\n" + err_trace)

    app = FastAPI(title="PocketSmart Error Fallback")

    @app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def vercel_import_error(path_name: str):
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "PocketSmart backend failed to initialize on Vercel.",
                "details": str(exc),
                "traceback": err_trace.splitlines(),
            },
        )