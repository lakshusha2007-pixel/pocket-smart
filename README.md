# PocketSmart — Your Smart Budget & Recommendation Assistant

**PocketSmart** is a cross-platform budget and recommendation application built with a **separated frontend and backend architecture**:
- **`backend/`**: High-performance FastAPI REST API, database models, Gemini foundation logic, and authentication.
- **`frontend/`**: Clean, human-designed UI with HTML5, Jinja2 templates, and responsive Vanilla CSS.

---

## 📁 Separated Folder Architecture

```
NM/
├── backend/                    # 🐍 BACKEND SERVICE LAYER
│   ├── main.py                 # FastAPI application & REST API routes
│   ├── database.py             # SQLite database & /tmp serverless handling
│   ├── gemini_utils.py         # Gemini prompt orchestration & retailer links
│   ├── recommender.py          # Domain catalogs (Home, Party, Jewelry) & budget logic
│   ├── auth_utils.py           # RFC 7519 HS256 JWT token generation & verification
│   ├── pocketsmart.db          # Database with preloaded demo data
│   ├── test_app.py             # Backend automated test suite (11 unit tests)
│   ├── requirements.txt        # Backend dependencies
│   ├── Dockerfile              # Backend container build
│   ├── Procfile                # Render start command
│   ├── .dockerignore
│   ├── .env.example
│   └── README.md
│
├── frontend/                   # 🎨 FRONTEND PRESENTATION LAYER
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css      # Design system stylesheet (Inter, #2563EB primary)
│   │   ├── js/
│   │   │   └── main.js         # Interactive calculators, steppers & modals
│   │   └── uploads/            # Uploaded outfit reference images
│   ├── templates/
│   │   ├── base.html           # Master layout template
│   │   ├── index.html          # Landing page & budget simulator
│   │   ├── dashboard.html      # Spending overview & active plans
│   │   ├── home_planner.html   # Home Interior budget planner
│   │   ├── party_planner.html  # Party & Event budget planner
│   │   ├── jewelry_planner.html# Fine Jewelry budget planner
│   │   ├── recommendations.html# Curated product cards & retailer links
│   │   ├── history.html        # Historical planning records
│   │   ├── login.html          # Authentication sign-in
│   │   └── register.html       # User registration
│   └── README.md
│
├── render.yaml                 # Render Blueprint (points to backend/)
├── vercel.json                 # Vercel deployment configuration
├── package.json                # Project scripts (dev, test, deploy)
└── README.md                   # Master documentation
```

---

## 🌟 Key Scenarios & Modules

1. **Home Interior Planning with Smart Budget Allocation (`/planner/home`, `/generate-home`)**:
   - Room-by-room budget allocation (Living Room, Bedroom, Kitchen, Office).
   - Quantity configuration for BLDC silent fans, drop pendant lights, sofas, solid wood dining tables, storage wardrobes, and wall art.
   - Sourced from **IKEA, Amazon, Pepperfry, and Urban Ladder**.

2. **Party Budget Planning (`/planner/party`, `/generate-party`)**:
   - Total budget allocation based on guest count, event type (Birthday, Anniversary, Corporate), and venue.
   - Automatic per-guest catering formulas (**Swiggy Catering / Zomato Events**), designer specialty cakes (**Ferns N Petals / Bakingo**), theme decor, and sound AV packages.

3. **Jewelry Recommendations for Occasions (`/planner/jewelry`, `/generate-jewelry`)**:
   - Outfit photo upload to analyze color coordination and neckline style.
   - Hallmarked gold, uncut Kundan Polki, diamonds, and 925 sterling silver from **Tanishq, CaratLane, Kalyan Jewellers, and GIVA**.

4. **Recommendation Engine & Verified Retailer Links (`/recommendations/{id}`)**:
   - Dynamic progress bars, remaining budget badges, category cost breakdowns, and 1-click **"Buy on Retailer"** deep links.

5. **User Dashboard & History (`/dashboard`, `/history`)**:
   - Real-time KPI cards (Active Plans, Total Budget Managed, Smart Savings Retained), plus saved query history.

6. **Authentication & JWT API (`/login`, `/register`, `/token`, `/session-info`, `/session-data`)**:
   - Session-based web auth + RFC 7519 HS256 JWT tokens for API clients.

---

## 🚀 Running the Project

### Option A: Run Full Stack from Root
```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Run development server (serves both backend API and frontend UI)
npm run dev
# OR:
python backend/main.py
```
Open **http://127.0.0.1:8080** or **http://localhost:8080** in your browser.

### Option B: Run Backend Only
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Option C: Run Automated Tests
```bash
# Run backend tests
python backend/test_app.py
# OR from root:
npm test
```
*Output: `Ran 11 tests in 0.55s — OK`*

---

## 🔑 Demo Account Credentials

- **Email**: `demo@pocketsmart.ai`
- **Password**: `demo1234`
*(Or register a new account on `/register`)*

---

## ☁️ Deployment Guide 1: Deploy Backend with Render CLI

The backend is configured with **`backend/Dockerfile`**, **`backend/Procfile`**, and root **`render.yaml`** (pointing to `rootDir: backend`).

```powershell
# 1. Install Render CLI
npm install -g @renderinc/cli

# 2. Login
render login

# 3. Deploy via Blueprint
git add .
git commit -m "Deploy separated backend"
git push origin main
render blueprint launch
```

---

## ▲ Deployment Guide 2: Deploy with Vercel CLI

The project is configured with **`vercel.json`** and **`api/index.py`**:

```powershell
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Link project
vercel link

# 4. Deploy to production
vercel --prod
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Main Landing Page with interactive Smart Budget Simulator & Testimonials |
| `GET` | `/dashboard` | User dashboard with budget KPIs and quick action cards |
| `GET/POST`| `/generate-home` | Home Interior Planner (accepts Form data or JSON) |
| `GET/POST`| `/generate-party` | Party Budget Planner (accepts Form data or JSON) |
| `GET/POST`| `/generate-jewelry` | Jewelry Planner (accepts Form data, JSON, or outfit photo upload) |
| `POST` | `/token` | Issues RFC 7519 HS256 JWT access token for API clients |
| `GET` | `/session-info` | Current user session metadata and login state |
| `GET` | `/session-data` | Detailed user session data, metrics, and plan history |
| `GET/POST`| `/recommendations-details` | General detailed product recommendations |
| `GET` | `/recommendations/{id}` | Detailed recommendation breakdown & verified retailer links |
| `GET` | `/history` | Historical planning records (HTML view or JSON API) |
| `GET` | `/health` / `/startup` | Health check and platform connectivity check |
