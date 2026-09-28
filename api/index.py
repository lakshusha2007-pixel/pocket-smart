# import sys
# import os

# ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, ROOT_DIR)

# from backend.main import app
import os
import sys
import traceback

from fastapi import FastAPI
from fastapi.responses import JSONResponse


# ---------------------------------------------------------
# Make project root available
# ---------------------------------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# ---------------------------------------------------------
# Create FastAPI FIRST
# ---------------------------------------------------------

app = FastAPI(
    title="PocketSmart",
    version="1.0.0"
)


# ---------------------------------------------------------
# Import real application safely
# ---------------------------------------------------------

IMPORT_ERROR = None
IMPORT_TRACEBACK = None

try:

    from backend.main import app as real_app

    # Copy the real FastAPI application
    app = real_app

except Exception as e:

    IMPORT_ERROR = repr(e)
    IMPORT_TRACEBACK = traceback.format_exc()

    print("==============================================")
    print("POCKETSMART IMPORT ERROR")
    print("==============================================")
    print(IMPORT_TRACEBACK)
    print("==============================================")


# ---------------------------------------------------------
# Diagnostic route
# ---------------------------------------------------------

@app.get("/vercel-debug")
async def vercel_debug():

    if IMPORT_ERROR:

        return JSONResponse(
            status_code=500,
            content={
                "status": "FAILED",
                "message": "backend.main could not be imported",
                "error": IMPORT_ERROR,
                "traceback": IMPORT_TRACEBACK
            }
        )

    return {
        "status": "OK",
        "message": "PocketSmart backend.main imported successfully"
    }


# ---------------------------------------------------------
# Fallback root
# ---------------------------------------------------------

@app.get("/vercel-test")
async def vercel_test():

    return {
        "status": "success",
        "message": "Vercel Python function is working",
        "backend_import_error": IMPORT_ERROR
    }