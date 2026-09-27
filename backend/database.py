import sqlite3
import os
import hashlib
import binascii
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "pocketsmart.db")

def get_database_path():
    # Detect Vercel / AWS Lambda serverless read-only filesystem
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        tmp_db = "/tmp/pocketsmart.db"
        if not os.path.exists(tmp_db) and os.path.exists(DEFAULT_DB_PATH):
            try:
                shutil.copy2(DEFAULT_DB_PATH, tmp_db)
            except Exception:
                pass
        return tmp_db

    # Verify write access to current directory
    try:
        test_file = os.path.join(BASE_DIR, ".write_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return DEFAULT_DB_PATH
    except Exception:
        tmp_dir = os.environ.get("TEMP", os.environ.get("TMP", "/tmp"))
        tmp_db = os.path.join(tmp_dir, "pocketsmart.db")
        if not os.path.exists(tmp_db) and os.path.exists(DEFAULT_DB_PATH):
            try:
                shutil.copy2(DEFAULT_DB_PATH, tmp_db)
            except Exception:
                pass
        return tmp_db

DB_PATH = get_database_path()

def get_db_connection():
    global DB_PATH
    # Ensure parent dir exists if needed
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password: str, provided_password: str) -> bool:
    salt = stored_password[:64]
    stored_hash = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_hash

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Planning history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS planning_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            planner_type TEXT NOT NULL,
            title TEXT NOT NULL,
            budget REAL NOT NULL,
            estimated_cost REAL NOT NULL,
            remaining REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Completed',
            inputs_json TEXT NOT NULL,
            recommendations_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Create default demo user if empty
    cursor.execute("SELECT id FROM users WHERE email = 'demo@pocketsmart.ai'")
    if not cursor.fetchone():
        demo_pwd_hash = hash_password("demo1234")
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Alex Johnson", "demo@pocketsmart.ai", demo_pwd_hash)
        )
        demo_user_id = cursor.lastrowid
        
        # Insert initial realistic sample history records
        sample_home_inputs = {
            "room_type": "Living Room",
            "budget": 50000,
            "items": {"lights": 4, "ceiling_fans": 2, "sofa": 1, "decorations": 3}
        }
        sample_home_recs = {
            "categories": [
                {"name": "Furniture", "amount": 26999},
                {"name": "Lighting", "amount": 6998},
                {"name": "Decor & Accents", "amount": 8200}
            ],
            "items": [
                {
                    "title": "Nordic 3-Seater Fabric Sofa",
                    "category": "Furniture",
                    "platform": "Pepperfry",
                    "price": 26999,
                    "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&auto=format&fit=crop&q=80",
                    "status": "Within Budget",
                    "reason": "Compact 3-seater living room centerpiece with durable linen upholstery and high-density foam cushions."
                },
                {
                    "title": "AeroPlus 1200mm BLDC Ceiling Fan (Pack of 2)",
                    "category": "Lighting",
                    "platform": "Amazon",
                    "price": 4998,
                    "image": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=600&auto=format&fit=crop&q=80",
                    "status": "Within Budget",
                    "reason": "Energy-efficient 5-star rated BLDC fans with whisper-silent motor and remote control."
                },
                {
                    "title": "Minimalist Matte Black Pendant Light (Pack of 2)",
                    "category": "Lighting",
                    "platform": "IKEA",
                    "price": 2000,
                    "image": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=600&auto=format&fit=crop&q=80",
                    "status": "Within Budget",
                    "reason": "Sleek industrial aluminum drop lights delivering warm ambient living room illumination."
                },
                {
                    "title": "Bohemian Hand-Woven Accent Rug & Cushions",
                    "category": "Decor & Accents",
                    "platform": "Urban Ladder",
                    "price": 8200,
                    "image": "https://images.unsplash.com/photo-1600121848594-d8644e57abab?w=600&auto=format&fit=crop&q=80",
                    "status": "Within Budget",
                    "reason": "Geometric pattern floor rug paired with textured linen throw pillow covers for comfortable seating."
                }
            ]
        }
        
        sample_party_inputs = {
            "event_type": "Birthday",
            "budget": 30000,
            "guest_count": 45,
            "venue": "Home Lounge / Backyard",
            "food_pref": "Buffet Dinner + Starters",
            "decor_pref": "Minimalist Pastel & Balloon Garland"
        }
        sample_party_recs = {
            "categories": [
                {"name": "Catering & Beverages", "amount": 18500},
                {"name": "Decorations & Theme", "amount": 5400},
                {"name": "Custom Cake & Desserts", "amount": 2800},
                {"name": "Audio & Lighting Setup", "amount": 2200}
            ],
            "items": [
                {
                    "title": "Deluxe Multi-Cuisine Live Buffet Package",
                    "category": "Catering",
                    "platform": "Swiggy Catering",
                    "price": 18500,
                    "image": "https://images.unsplash.com/photo-1555244162-803834f70033?w=600&auto=format&fit=crop&q=80",
                    "status": "Within Budget",
                    "reason": "4-course buffet catering including 2 starters, 3 main entrees, bread basket, and beverage station."
                },
                {
                    "title": "Organic Arch Balloon Archway & Fairy Lights",
                    "category": "Decorations",
                    "platform": "PartyMania",
                    "price": 5400,
                    "image": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=600&auto=format&fit=crop&q=80",
                    "status": "Within Budget",
                    "reason": "Curated pastel balloon styling backdrop with warm LED ambient fairy lights and customized welcome board."
                },
                {
                    "title": "2-Tier Belgian Truffle Artisan Cake (2.5 Kg)",
                    "category": "Desserts",
                    "platform": "Ferns N Petals",
                    "price": 2800,
                    "image": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&auto=format&fit=crop&q=80",
                    "status": "Within Budget",
                    "reason": "Handcrafted layered Dutch dark chocolate birthday cake with custom lettering and fresh floral toppers."
                },
                {
                    "title": "High-Fidelity Bluetooth PA Speaker & Wireless Mic",
                    "category": "Audio",
                    "platform": "Amazon",
                    "price": 2200,
                    "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80",
                    "status": "Within Budget",
                    "reason": "100W portable sound system providing crisp music playback and microphone support for speeches."
                }
            ]
        }
        
        cursor.execute("""
            INSERT INTO planning_history (user_id, planner_type, title, budget, estimated_cost, remaining, status, inputs_json, recommendations_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            demo_user_id,
            "Home Interior",
            "Living Room Makeover",
            50000,
            42197,
            7803,
            "Completed",
            json.dumps(sample_home_inputs),
            json.dumps(sample_home_recs),
            "2026-09-25 14:30:00"
        ))
        
        cursor.execute("""
            INSERT INTO planning_history (user_id, planner_type, title, budget, estimated_cost, remaining, status, inputs_json, recommendations_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            demo_user_id,
            "Party Budget",
            "30th Birthday Celebration",
            30000,
            28900,
            1100,
            "Completed",
            json.dumps(sample_party_inputs),
            json.dumps(sample_party_recs),
            "2026-09-26 10:15:00"
        ))
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
