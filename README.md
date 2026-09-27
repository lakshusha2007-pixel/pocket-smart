# PocketSmart AI — Your Smart Budget & Recommendation Assistant

**PocketSmart AI** is a GenAI-powered, cross-platform recommendation SaaS application built with **FastAPI**, **Google Gemini 1.5 Flash Pro**, **Jinja2**, and **Vanilla CSS**. It transforms everyday lifestyle budgeting into an intelligent, user-friendly experience by delivering personalized, budget-strict product and service suggestions across multiple retail ecosystems: **Amazon, Flipkart, IKEA, Pepperfry, Urban Ladder, Swiggy, Zomato, OYO, Tanishq, CaratLane, and GIVA**.

---

## 🌟 Key Scenarios & Modules

1. **Home Interior Planning with Smart Budget Allocation (`/planner/home`, `/generate-home`)**:
   - Room-by-room budget allocation (Living Room, Bedroom, Kitchen, Office).
   - Quantity configuration for BLDC silent fans, drop pendant lights, sofas, solid wood dining tables, storage wardrobes, and wall art.
   - Sourced from **IKEA, Amazon, Pepperfry, and Urban Ladder**.

2. **AI-Based Party Budget Planning (`/planner/party`, `/generate-party`)**:
   - Total budget allocation based on guest count, event type (Birthday, Anniversary, Corporate), and venue.
   - Automatic per-guest catering formulas (**Swiggy Catering / Zomato Events**), designer specialty cakes (**Ferns N Petals / Bakingo**), theme decor, and sound AV packages.

3. **Jewelry Recommendations for Occasions (`/planner/jewelry`, `/generate-jewelry`)**:
   - Multimodal AI: Upload outfit photos to analyze palette harmony, neckline aesthetics, and metal accents.
   - Hallmarked gold, uncut Kundan Polki, diamonds, and 925 sterling silver from **Tanishq, CaratLane, Kalyan Jewellers, and GIVA**.

4. **Recommendation Engine & Verified Retailer Links (`/recommendations/{id}`)**:
   - Dynamic progress bars, remaining budget badges, category cost breakdowns, and 1-click **"Buy on Retailer"** deep links.

5. **User Dashboard & History (`/dashboard`, `/history`)**:
   - Real-time KPI cards (Active Plans, Total Budget Managed, Smart Savings Retained), plus saved query history.

6. **Authentication & JWT API (`/login`, `/register`, `/token`, `/session-info`, `/session-data`)**:
   - Session-based web auth + RFC 7519 HS256 JWT tokens for API clients.

---

## 🏗️ Architecture & Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.10+) | High-performance asynchronous REST & template routing |
| **AI Foundation Model** | Google Gemini 1.5 Flash Pro | Multimodal text & image reasoning with fallback catalog |
| **Frontend UI** | HTML5, Jinja2, Vanilla CSS, JS | Zero-gradient enterprise design system, Inter typography |
| **Database** | SQLite3 (`pocketsmart.db`) | Automatic `/tmp` migration for serverless (Vercel) & local |
| **Deployments** | Render CLI & Vercel CLI | Native support with `render.yaml`, `Procfile`, `vercel.json` |

---

## 🚀 Local Development Setup

### 1. Clone & Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# Optional: add your Gemini API key (free from https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here
SESSION_SECRET=your_super_secret_session_key
PORT=8080
```
*(Note: If `GEMINI_API_KEY` is not provided, the system gracefully falls back to the deterministic catalog engine with realistic platform links!)*

### 3. Run Application
```bash
python main.py
```
Or with Uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```
Access the application at **http://127.0.0.1:8080**.

### 4. Run Automated Test Suite
```bash
python test_app.py
```

---

## 🔑 Demo Account Credentials

- **Email**: `demo@pocketsmart.ai`
- **Password**: `demo1234`
*(Or register a new account on `/register`)*

---

## ☁️ Deployment Guide 1: Deploy with Render CLI

PocketSmart AI includes **`render.yaml`** (Render Blueprint), **`Procfile`**, and **`Dockerfile`** for 1-click deployment on Render.

### Method A: Using Render CLI (Recommended)

1. **Install Render CLI**:
   ```bash
   npm install -g @renderinc/cli
   ```
   *(Or download binary from [render.com/docs/cli](https://render.com/docs/cli))*

2. **Authenticate with Render**:
   ```bash
   render login
   ```

3. **Deploy using Render Blueprint (`render.yaml`)**:
   Make sure your code is committed to a Git repository (GitHub/GitLab):
   ```bash
   git add .
   git commit -m "Configure PocketSmart AI for Render and Vercel"
   git push origin main
   ```
   Then launch the blueprint:
   ```bash
   render blueprint launch
   ```

4. **Or Create Web Service Directly via Render CLI**:
   ```bash
   render services create \
     --name pocketsmart-ai \
     --type web \
     --runtime python \
     --repo <YOUR_GITHUB_REPO_URL> \
     --branch main \
     --buildCommand "pip install -r requirements.txt" \
     --startCommand "uvicorn main:app --host 0.0.0.0 --port \$PORT"
   ```

5. **Set Environment Variables on Render**:
   ```bash
   render env-vars set GEMINI_API_KEY your_gemini_api_key_here
   render env-vars set SESSION_SECRET a_very_long_secure_random_string_9912
   ```

6. **View Deployment Logs**:
   ```bash
   render logs -s pocketsmart-ai --tail
   ```

---

## ▲ Deployment Guide 2: Deploy with Vercel CLI

PocketSmart AI is pre-configured with **`vercel.json`**, **`api/index.py`**, and **serverless `/tmp` database path management** for seamless zero-config deployment on Vercel.

### Step-by-Step Vercel CLI Instructions

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Link Your Project**:
   Run in the project directory (`NM`):
   ```bash
   vercel link
   ```
   Follow the prompts to connect or create a new Vercel project.

4. **Add Environment Variables (Optional for Gemini)**:
   ```bash
   vercel env add GEMINI_API_KEY
   # Select 'Production', 'Preview', and 'Development', then enter your key
   ```

5. **Deploy Preview**:
   ```bash
   vercel
   ```

6. **Deploy Directly to Production**:
   ```bash
   vercel --prod
   ```

7. **Inspect Deployment**:
   ```bash
   vercel inspect --prod
   ```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Main Landing Page with interactive Smart Budget Simulator & Testimonials |
| `GET` | `/dashboard` | User dashboard with budget KPIs and quick action cards |
| `GET/POST`| `/generate-home` | Home Interior Planner (accepts Form data or JSON) |
| `GET/POST`| `/generate-party` | Party Budget Planner (accepts Form data or JSON) |
| `GET/POST`| `/generate-jewelry` | Multimodal Jewelry Planner (accepts Form data, JSON, or outfit photo upload) |
| `POST` | `/token` | Issues RFC 7519 HS256 JWT access token for API clients |
| `GET` | `/session-info` | Current user session metadata and login state |
| `GET` | `/session-data` | Detailed user session data, metrics, and plan history |
| `GET/POST`| `/recommendations-details` | General detailed AI product recommendations |
| `GET` | `/recommendations/{id}` | Detailed recommendation breakdown & verified retailer links |
| `GET` | `/history` | Historical planning records (HTML view or JSON API) |
| `GET` | `/health` / `/startup` | Health check, Gemini AI connection test, and database status |
