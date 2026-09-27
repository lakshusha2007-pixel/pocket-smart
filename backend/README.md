# PocketSmart — Backend

This directory contains the core service layer, REST API endpoints, recommendation engine, database access, and authentication for **PocketSmart**.

---

## 📁 Directory Structure

```
backend/
├── main.py              # FastAPI application, route handlers, session & CORS setup
├── database.py          # SQLite database connection & automated /tmp serverless handling
├── gemini_utils.py      # Google Gemini 1.5 Flash Pro prompt orchestration & retailer links
├── recommender.py       # Domain catalogs (Home, Party, Jewelry) & budget optimization
├── auth_utils.py        # RFC 7519 HS256 JWT token generation & validation
├── pocketsmart.db       # Seed database with demo user & historical plans
├── test_app.py          # Automated test suite (11 unit tests)
├── requirements.txt     # Python dependencies
├── Dockerfile           # Production container build
├── Procfile             # Render web process definition
└── .env.example         # Environment variables template
```

---

## 🚀 Running the Backend

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Uvicorn Server
```bash
python main.py
```
Or with Uvicorn directly:
```bash
uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```
The server will start at **http://127.0.0.1:8080**.

### 3. Run Automated Tests
```bash
python test_app.py
```

---

## 📡 Key REST API Endpoints

- `POST /generate-home`: Home interior recommendation generator
- `POST /generate-party`: Party budget recommendation generator
- `POST /generate-jewelry`: Multimodal jewelry recommendation generator
- `POST /token`: Issue JWT bearer token for API clients
- `GET /session-info`: Current session metadata
- `GET /session-data`: Detailed session metrics and history
- `GET /recommendations-details`: Detailed recommendation query
- `GET /history`: User planning records
- `GET /health`: Health and platform connectivity check
