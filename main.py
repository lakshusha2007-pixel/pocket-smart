import os
import json
import uuid
import shutil
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, HTTPException, status, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from database import (
    init_db, hash_password, verify_password,
    get_user_by_id, get_user_by_email, create_user,
    create_planning_history, get_user_planning_history,
    get_planning_history_by_id, delete_planning_history,
    get_user_stats, is_db_connected, get_db_connection
)
import recommender
import gemini_utils
import auth_utils
# ==================== DIRECTORIES ====================

# main.py is inside /backend, so move one level up to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Frontend directories
TEMPLATES_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

# Fallback if frontend is located differently
if not os.path.isdir(TEMPLATES_DIR):
    TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

if not os.path.isdir(STATIC_DIR):
    STATIC_DIR = os.path.join(BASE_DIR, "static")

# Vercel filesystem is read-only except /tmp
if os.environ.get("VERCEL"):
    UPLOADS_DIR = "/tmp/uploads"
else:
    UPLOADS_DIR = os.path.join(STATIC_DIR, "uploads")

# Only create the writable upload directory
os.makedirs(UPLOADS_DIR, exist_ok=True)

print(f"BASE_DIR: {BASE_DIR}")
print(f"TEMPLATES_DIR: {TEMPLATES_DIR}")
print(f"STATIC_DIR: {STATIC_DIR}")
print(f"UPLOADS_DIR: {UPLOADS_DIR}")
# Initialize Database (Firebase Firestore / Fallback)
init_db()

app = FastAPI(
    title="PocketSmart",
    description="Smart Budget & Recommendation Assistant powered by FastAPI, Firebase Cloud Firestore and Google Gemini",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Middleware
SECRET_KEY = os.environ.get("SESSION_SECRET", "pocketsmart-secure-session-key-random-string-9912")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=86400 * 7)

# Mount Static Files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

def render(request: Request, template_name: str, context: dict = None):
    ctx = {"request": request}
    if context:
        ctx.update(context)
    return templates.TemplateResponse(request=request, name=template_name, context=ctx)

# Helper function to get current user from Session or Authorization Bearer token
def get_current_user(request: Request):
    # 1. Try session
    user_id = request.session.get("user_id")
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            return {"id": user["id"], "name": user["name"], "email": user["email"]}

    # 2. Try Authorization Bearer header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = auth_utils.verify_jwt_token(token)
        if payload and "sub" in payload:
            user = get_user_by_id(payload["sub"])
            if user:
                return {"id": user["id"], "name": user["name"], "email": user["email"]}

    return None

def is_json_request(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    content_type = request.headers.get("content-type", "")
    return "application/json" in accept or "application/json" in content_type

# ==================== LANDING & AUTHENTICATION ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user = get_current_user(request)
    return render(request, "index.html", {
        "user": user,
        "active_tab": "home",
        "title": "PocketSmart — Smart Budget & Recommendation Assistant"
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    error = request.session.pop("flash_error", None)
    message = request.session.pop("flash_message", None)
    return render(request, "login.html", {
        "error": error,
        "message": message,
        "title": "Sign In — PocketSmart"
    })

@app.post("/login")
async def handle_login(request: Request, email: str = Form(None), password: str = Form(None)):
    if is_json_request(request) and not email:
        try:
            body = await request.json()
            email = body.get("email")
            password = body.get("password")
        except Exception:
            pass

    if not email or not password:
        if is_json_request(request):
            return JSONResponse(status_code=400, content={"error": "Email and password are required."})
        return render(request, "login.html", {
            "error": "Email and password are required.",
            "title": "Sign In — PocketSmart"
        })

    user = get_user_by_email(email.strip().lower())

    if not user or not verify_password(user.get("password_hash", ""), password):
        if is_json_request(request):
            return JSONResponse(status_code=401, content={"error": "Invalid email address or password."})
        return render(request, "login.html", {
            "error": "Invalid email address or password. Please try again.",
            "email": email,
            "title": "Sign In — PocketSmart"
        })

    request.session["user_id"] = user["id"]
    request.session["user_name"] = user["name"]
    request.session["user_email"] = user["email"]

    if is_json_request(request):
        token = auth_utils.create_jwt_token({"sub": user["id"], "email": user["email"], "name": user["name"]})
        return JSONResponse({
            "status": "success",
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": user["id"], "name": user["name"], "email": user["email"]}
        })

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    error = request.session.pop("flash_error", None)
    return render(request, "register.html", {
        "error": error,
        "title": "Create Account — PocketSmart"
    })

@app.post("/register")
async def handle_register(
    request: Request,
    name: str = Form(None),
    email: str = Form(None),
    password: str = Form(None),
    confirm_password: str = Form(None)
):
    if is_json_request(request) and not name:
        try:
            body = await request.json()
            name = body.get("name")
            email = body.get("email")
            password = body.get("password")
            confirm_password = body.get("confirm_password", password)
        except Exception:
            pass

    if not name or not email or not password:
        err = "All fields are required."
        if is_json_request(request):
            return JSONResponse(status_code=400, content={"error": err})
        return render(request, "register.html", {"error": err, "name": name, "email": email, "title": "Create Account — PocketSmart"})

    if password != confirm_password:
        err = "Passwords do not match."
        if is_json_request(request):
            return JSONResponse(status_code=400, content={"error": err})
        return render(request, "register.html", {"error": err, "name": name, "email": email, "title": "Create Account — PocketSmart"})

    if len(password) < 6:
        err = "Password must be at least 6 characters."
        if is_json_request(request):
            return JSONResponse(status_code=400, content={"error": err})
        return render(request, "register.html", {"error": err, "name": name, "email": email, "title": "Create Account — PocketSmart"})

    existing = get_user_by_email(email.strip().lower())
    if existing:
        err = "An account with this email already exists."
        if is_json_request(request):
            return JSONResponse(status_code=400, content={"error": err})
        return render(request, "register.html", {"error": err, "name": name, "title": "Create Account — PocketSmart"})

    pwd_hash = hash_password(password)
    user = create_user(name.strip(), email.strip().lower(), pwd_hash)
    user_id = user["id"]

    request.session["user_id"] = user_id
    request.session["user_name"] = name.strip()
    request.session["user_email"] = email.strip().lower()

    if is_json_request(request):
        token = auth_utils.create_jwt_token({"sub": user_id, "email": email.strip().lower(), "name": name.strip()})
        return JSONResponse(status_code=201, content={
            "status": "success",
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": user_id, "name": name.strip(), "email": email.strip().lower()}
        })

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

# Token & Session Endpoints
@app.post("/token")
async def issue_token(request: Request, username: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    email = username
    if not email:
        try:
            body = await request.json()
            email = body.get("username") or body.get("email")
            password = body.get("password")
        except Exception:
            pass

    if not email or not password:
        raise HTTPException(status_code=400, detail="Username/email and password required")

    user = get_user_by_email(email.strip().lower())

    if not user or not verify_password(user.get("password_hash", ""), password):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    token = auth_utils.create_jwt_token({"sub": user["id"], "email": user["email"], "name": user["name"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }

@app.get("/session-info")
async def get_session_info(request: Request):
    user = get_current_user(request)
    if user:
        return {
            "is_authenticated": True,
            "user_id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    return {
        "is_authenticated": False,
        "user_id": None,
        "name": None,
        "email": None
    }

@app.get("/session-data")
async def get_session_data(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized. Please log in."})

    stats = get_user_stats(user["id"])
    recent = get_user_planning_history(user["id"], limit=5)

    return {
        "user": user,
        "metrics": {
            "total_plans": stats["total_plans"],
            "total_budgeted": stats["total_budgeted"],
            "total_saved": stats["total_saved"]
        },
        "recent_plans": recent
    }

# ==================== DASHBOARD ROUTE ====================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    stats = get_user_stats(user["id"])
    recent_history = get_user_planning_history(user["id"], limit=5)

    return render(request, "dashboard.html", {
        "user": user,
        "active_tab": "dashboard",
        "stats": stats,
        "recent_history": recent_history,
        "title": "Dashboard — PocketSmart"
    })

# ==================== PLANNER: HOME INTERIOR ====================

@app.get("/planner/home", response_class=HTMLResponse)
@app.get("/generate-home", response_class=HTMLResponse)
async def home_planner_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    return render(request, "home_planner.html", {
        "user": user,
        "active_tab": "home_planner",
        "title": "Home Interior Planner — PocketSmart"
    })

@app.post("/planner/home")
@app.post("/generate-home")
async def handle_home_planner(
    request: Request,
    budget: float = Form(50000.0),
    room_type: str = Form("Living Room"),
    lights: int = Form(4),
    ceiling_fans: int = Form(2),
    dining_table: int = Form(1),
    sofa: int = Form(1),
    storage: int = Form(1),
    decorations: int = Form(2)
):
    user = get_current_user(request)
    if not user and not is_json_request(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    if is_json_request(request) and budget == 50000.0:
        try:
            body = await request.json()
            budget = float(body.get("budget", 50000.0))
            room_type = body.get("room_type", "Living Room")
            items = body.get("items", {})
            lights = items.get("lights", 4)
            ceiling_fans = items.get("ceiling_fans", 2)
            dining_table = items.get("dining_table", 1)
            sofa = items.get("sofa", 1)
            storage = items.get("storage", 1)
            decorations = items.get("decorations", 2)
        except Exception:
            pass

    input_data = {
        "budget": budget,
        "room_type": room_type,
        "items": {
            "lights": lights,
            "ceiling_fans": ceiling_fans,
            "dining_table": dining_table,
            "sofa": sofa,
            "storage": storage,
            "decorations": decorations
        }
    }

    result = gemini_utils.generate_home_recommendations(input_data)

    history_id = None
    if user:
        history_id = create_planning_history(
            user_id=user["id"],
            planner_type="Home Interior",
            title=f"{room_type} Interior Plan",
            budget=result["budget"],
            estimated_cost=result["estimated_total"],
            remaining=result["remaining"],
            status=result["status"],
            inputs_json=input_data,
            recommendations_json=result
        )

    if is_json_request(request):
        return JSONResponse({
            "status": "success",
            "history_id": history_id,
            "data": result
        })

    return RedirectResponse(url=f"/recommendations/{history_id}", status_code=status.HTTP_302_FOUND)

# ==================== PLANNER: PARTY ====================

@app.get("/planner/party", response_class=HTMLResponse)
@app.get("/generate-party", response_class=HTMLResponse)
async def party_planner_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    return render(request, "party_planner.html", {
        "user": user,
        "active_tab": "party_planner",
        "title": "Party Budget Planner — PocketSmart"
    })

@app.post("/planner/party")
@app.post("/generate-party")
async def handle_party_planner(
    request: Request,
    budget: float = Form(30000.0),
    guest_count: int = Form(40),
    event_type: str = Form("Birthday"),
    venue: str = Form("Home / Backyard"),
    food_pref: str = Form("Buffet Dinner"),
    decor_pref: str = Form("Balloon Theme")
):
    user = get_current_user(request)
    if not user and not is_json_request(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    if is_json_request(request) and budget == 30000.0:
        try:
            body = await request.json()
            budget = float(body.get("budget", 30000.0))
            guest_count = int(body.get("guest_count", 40))
            event_type = body.get("event_type", "Birthday")
            venue = body.get("venue", "Home / Backyard")
            food_pref = body.get("food_pref", "Buffet Dinner")
            decor_pref = body.get("decor_pref", "Balloon Theme")
        except Exception:
            pass

    input_data = {
        "budget": budget,
        "guest_count": guest_count,
        "event_type": event_type,
        "venue": venue,
        "food_pref": food_pref,
        "decor_pref": decor_pref
    }

    result = gemini_utils.generate_party_recommendations(input_data)

    history_id = None
    if user:
        history_id = create_planning_history(
            user_id=user["id"],
            planner_type="Party Planner",
            title=f"{event_type} Party Budget",
            budget=result["budget"],
            estimated_cost=result["estimated_total"],
            remaining=result["remaining"],
            status=result["status"],
            inputs_json=input_data,
            recommendations_json=result
        )

    if is_json_request(request):
        return JSONResponse({
            "status": "success",
            "history_id": history_id,
            "data": result
        })

    return RedirectResponse(url=f"/recommendations/{history_id}", status_code=status.HTTP_302_FOUND)

# ==================== PLANNER: JEWELRY (MULTIMODAL) ====================

@app.get("/planner/jewelry", response_class=HTMLResponse)
@app.get("/generate-jewelry", response_class=HTMLResponse)
async def jewelry_planner_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    return render(request, "jewelry_planner.html", {
        "user": user,
        "active_tab": "jewelry_planner",
        "title": "Jewelry Budget Planner — PocketSmart"
    })

@app.post("/planner/jewelry")
@app.post("/generate-jewelry")
async def handle_jewelry_planner(
    request: Request,
    budget: float = Form(25000.0),
    occasion: str = Form("Wedding"),
    jewelry_type: str = Form("All"),
    preferred_style: str = Form("Traditional"),
    color_pref: str = Form("Gold"),
    outfit_image: UploadFile = File(None)
):
    user = get_current_user(request)
    if not user and not is_json_request(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    image_bytes = None
    saved_image_url = None

    if outfit_image and outfit_image.filename:
        ext = os.path.splitext(outfit_image.filename)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.webp']:
            file_name = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(UPLOADS_DIR, file_name)
            try:
                image_bytes = await outfit_image.read()
                with open(file_path, "wb") as buffer:
                    buffer.write(image_bytes)
                saved_image_url = f"/static/uploads/{file_name}"
            except Exception as e:
                print(f"Error saving image upload: {e}")

    # Support JSON payload
    if is_json_request(request) and budget == 25000.0 and not outfit_image:
        try:
            body = await request.json()
            budget = float(body.get("budget", 25000.0))
            occasion = body.get("occasion", "Wedding")
            jewelry_type = body.get("jewelry_type", "All")
            preferred_style = body.get("preferred_style", "Traditional")
            color_pref = body.get("color_pref", "Gold")
            saved_image_url = body.get("outfit_image", None)
        except Exception:
            pass

    input_data = {
        "budget": budget,
        "occasion": occasion,
        "jewelry_type": jewelry_type,
        "preferred_style": preferred_style,
        "color_pref": color_pref,
        "outfit_image": saved_image_url
    }

    result = gemini_utils.generate_jewelry_recommendations(input_data, outfit_image_bytes=image_bytes)

    history_id = None
    if user:
        history_id = create_planning_history(
            user_id=user["id"],
            planner_type="Jewelry Planner",
            title=f"{occasion} {preferred_style} Jewelry",
            budget=result["budget"],
            estimated_cost=result["estimated_total"],
            remaining=result["remaining"],
            status=result["status"],
            inputs_json=input_data,
            recommendations_json=result
        )

    if is_json_request(request):
        return JSONResponse({
            "status": "success",
            "history_id": history_id,
            "data": result
        })

    return RedirectResponse(url=f"/recommendations/{history_id}", status_code=status.HTTP_302_FOUND)

@app.post("/recommendations-details")
@app.get("/recommendations-details")
async def recommendations_details(
    request: Request,
    category: str = "home",
    budget: float = 50000.0
):
    if request.method == "POST":
        try:
            body = await request.json()
            category = body.get("category", category)
            budget = float(body.get("budget", budget))
        except Exception:
            pass

    cat_clean = category.lower()
    if "home" in cat_clean:
        res = gemini_utils.generate_home_recommendations({"budget": budget, "room_type": "Living Room", "items": {"sofa": 1, "lights": 4}})
    elif "party" in cat_clean:
        res = gemini_utils.generate_party_recommendations({"budget": budget, "guest_count": 40, "event_type": "Celebration"})
    else:
        res = gemini_utils.generate_jewelry_recommendations({"budget": budget, "occasion": "Festival", "preferred_style": "Traditional"})

    return JSONResponse({"status": "success", "category": category, "budget": budget, "recommendations": res})

# ==================== RECOMMENDATION RESULTS ====================

@app.get("/recommendations/{history_id}", response_class=HTMLResponse)
async def view_recommendations(request: Request, history_id: str):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    record = get_planning_history_by_id(history_id, user_id=user["id"])
    if not record:
        raise HTTPException(status_code=404, detail="Planning record not found")

    rec_data = json.loads(record["recommendations_json"]) if isinstance(record["recommendations_json"], str) else record["recommendations_json"]
    inputs_data = json.loads(record["inputs_json"]) if isinstance(record["inputs_json"], str) else record["inputs_json"]

    if "items" in rec_data:
        rec_data["items"] = gemini_utils.enrich_items_with_links(rec_data["items"])

    budget = record["budget"]
    estimated_total = record["estimated_cost"]
    used_percentage = min(100, round((estimated_total / budget) * 100, 1)) if budget > 0 else 100

    return render(request, "recommendations.html", {
        "user": user,
        "record": record,
        "rec": rec_data,
        "inputs": inputs_data,
        "used_percentage": used_percentage,
        "title": f"Recommendations: {record['title']} — PocketSmart"
    })

# ==================== HISTORY ROUTE ====================

@app.get("/history")
async def history_page(request: Request):
    user = get_current_user(request)
    if not user:
        if is_json_request(request):
            return JSONResponse(status_code=401, content={"error": "Unauthorized"})
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    history_list = get_user_planning_history(user["id"])

    if is_json_request(request):
        return JSONResponse({"status": "success", "count": len(history_list), "history": history_list})

    return render(request, "history.html", {
        "user": user,
        "active_tab": "history",
        "history": history_list,
        "title": "Recommendation History — PocketSmart"
    })

@app.post("/history/delete/{history_id}")
async def delete_history_item(request: Request, history_id: str):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    delete_planning_history(history_id, user["id"])
    return RedirectResponse(url="/history", status_code=status.HTTP_302_FOUND)

# Startup & Health Diagnostic Endpoint
@app.get("/startup")
@app.get("/health")
async def startup_check():
    gemini_status = gemini_utils.validate_gemini_connection()
    db_ok = is_db_connected()

    return {
        "status": "online",
        "app": "PocketSmart",
        "database_connected": db_ok,
        "database_type": "Firebase Cloud Firestore",
        "gemini_ai": gemini_status,
        "supported_platforms": [
            "Amazon", "Flipkart", "IKEA", "Pepperfry", "Urban Ladder",
            "Swiggy Catering", "Zomato Events", "OYO", "Tanishq",
            "CaratLane", "GIVA", "Kalyan Jewellers", "Ferns N Petals", "Bakingo"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0" if os.environ.get("RENDER") or (os.environ.get("PORT") and not os.name == 'nt') else "127.0.0.1")
    print(f"\n=======================================================")
    print(f"  PocketSmart is running with Firebase Firestore!")
    print(f"  Open in browser: http://127.0.0.1:{port} or http://localhost:{port}")
    print(f"=======================================================")
    uvicorn.run("main:app", host=host, port=port, reload=True)
