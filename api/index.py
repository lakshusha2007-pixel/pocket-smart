# # # import sys
# # # import os

# # # ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# # # sys.path.insert(0, ROOT_DIR)

# # # from backend.main import app
# # import os
# # import sys
# # import traceback

# # from fastapi import FastAPI
# # from fastapi.responses import JSONResponse


# # # ---------------------------------------------------------
# # # Make project root available
# # # ---------------------------------------------------------

# # CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# # ROOT_DIR = os.path.dirname(CURRENT_DIR)

# # if ROOT_DIR not in sys.path:
# #     sys.path.insert(0, ROOT_DIR)


# # # ---------------------------------------------------------
# # # Create FastAPI FIRST
# # # ---------------------------------------------------------

# # app = FastAPI(
# #     title="PocketSmart",
# #     version="1.0.0"
# # )


# # # ---------------------------------------------------------
# # # Import real application safely
# # # ---------------------------------------------------------

# # IMPORT_ERROR = None
# # IMPORT_TRACEBACK = None

# # try:

# #     from backend.main import app as real_app

# #     # Copy the real FastAPI application
# #     app = real_app

# # except Exception as e:

# #     IMPORT_ERROR = repr(e)
# #     IMPORT_TRACEBACK = traceback.format_exc()

# #     print("==============================================")
# #     print("POCKETSMART IMPORT ERROR")
# #     print("==============================================")
# #     print(IMPORT_TRACEBACK)
# #     print("==============================================")


# # # ---------------------------------------------------------
# # # Diagnostic route
# # # ---------------------------------------------------------

# # @app.get("/vercel-debug")
# # async def vercel_debug():

# #     if IMPORT_ERROR:

# #         return JSONResponse(
# #             status_code=500,
# #             content={
# #                 "status": "FAILED",
# #                 "message": "backend.main could not be imported",
# #                 "error": IMPORT_ERROR,
# #                 "traceback": IMPORT_TRACEBACK
# #             }
# #         )

# #     return {
# #         "status": "OK",
# #         "message": "PocketSmart backend.main imported successfully"
# #     }


# # # ---------------------------------------------------------
# # # Fallback root
# # # ---------------------------------------------------------

# # @app.get("/vercel-test")
# # async def vercel_test():

# #     return {
# #         "status": "success",
# #         "message": "Vercel Python function is working",
# #         "backend_import_error": IMPORT_ERROR
# #     }

# import os
# import sys
# import traceback

# from fastapi import FastAPI
# from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles


# # ---------------------------------------------------------
# # Project directories
# # ---------------------------------------------------------

# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# ROOT_DIR = os.path.dirname(CURRENT_DIR)

# FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
# STATIC_DIR = os.path.join(FRONTEND_DIR, "static")


# # ---------------------------------------------------------
# # Make project root available
# # ---------------------------------------------------------

# if ROOT_DIR not in sys.path:
#     sys.path.insert(0, ROOT_DIR)


# # ---------------------------------------------------------
# # Create FastAPI application
# # ---------------------------------------------------------

# app = FastAPI(
#     title="PocketSmart",
#     version="1.0.0"
# )


# # ---------------------------------------------------------
# # Mount frontend static files
# #
# # Your CSS:
# # frontend/static/css/styles.css
# #
# # Will be available at:
# # /static/css/styles.css
# # ---------------------------------------------------------

# if os.path.isdir(STATIC_DIR):
#     app.mount(
#         "/static",
#         StaticFiles(directory=STATIC_DIR),
#         name="static"
#     )
# else:
#     print("WARNING: Static directory not found:")
#     print(STATIC_DIR)


# # ---------------------------------------------------------
# # Import real application safely
# # ---------------------------------------------------------

# IMPORT_ERROR = None
# IMPORT_TRACEBACK = None

# try:
#     from backend.main import app as real_app

#     # Use the real FastAPI application
#     app = real_app

#     # -----------------------------------------------------
#     # Mount static files on the real application too
#     # -----------------------------------------------------
#     if os.path.isdir(STATIC_DIR):

#         # Avoid mounting twice if backend.main already
#         # mounts /static.
#         existing_static_mount = any(
#             getattr(route, "path", None) == "/static"
#             for route in app.routes
#         )

#         if not existing_static_mount:
#             app.mount(
#                 "/static",
#                 StaticFiles(directory=STATIC_DIR),
#                 name="static"
#             )

# except Exception as e:

#     IMPORT_ERROR = repr(e)
#     IMPORT_TRACEBACK = traceback.format_exc()

#     print("==============================================")
#     print("POCKETSMART IMPORT ERROR")
#     print("==============================================")
#     print(IMPORT_TRACEBACK)
#     print("==============================================")


# # ---------------------------------------------------------
# # Diagnostic route
# # ---------------------------------------------------------

# @app.get("/vercel-debug")
# async def vercel_debug():

#     if IMPORT_ERROR:

#         return JSONResponse(
#             status_code=500,
#             content={
#                 "status": "FAILED",
#                 "message": "backend.main could not be imported",
#                 "error": IMPORT_ERROR,
#                 "traceback": IMPORT_TRACEBACK
#             }
#         )

#     return {
#         "status": "OK",
#         "message": "PocketSmart backend.main imported successfully",
#         "static_directory": STATIC_DIR,
#         "static_directory_exists": os.path.isdir(STATIC_DIR)
#     }


# # ---------------------------------------------------------
# # Static CSS diagnostic route
# # ---------------------------------------------------------

# @app.get("/css-test")
# async def css_test():

#     css_file = os.path.join(
#         STATIC_DIR,
#         "css",
#         "styles.css"
#     )

#     return {
#         "status": "success",
#         "css_file": css_file,
#         "css_exists": os.path.isfile(css_file)
#     }


# # ---------------------------------------------------------
# # Fallback test route
# # ---------------------------------------------------------

# @app.get("/vercel-test")
# async def vercel_test():

#     return {
#         "status": "success",
#         "message": "Vercel Python function is working",
#         "backend_import_error": IMPORT_ERROR
#     }


import os
from pathlib import Path

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"

# Upload directory
if os.environ.get("VERCEL"):
    UPLOADS_DIR = Path("/tmp/uploads")
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
else:
    UPLOADS_DIR = STATIC_DIR / "uploads"
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)