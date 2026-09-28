import os
import json
import hashlib
import binascii
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR) if os.path.basename(BASE_DIR) == "backend" else BASE_DIR

# Global Firestore client and state
_firestore_client = None
_db_mode = "uninitialized"  # "firestore" or "local_memory"

# In-memory collections used when Firebase credentials are not yet supplied
_local_db = {
    "users": {},           # doc_id -> dict
    "planning_history": {} # doc_id -> dict
}

def hash_password(password: str) -> str:
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password: str, provided_password: str) -> bool:
    if not stored_password or len(stored_password) < 64:
        return False
    salt = stored_password[:64]
    stored_hash = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_hash

def _find_service_account_path() -> Optional[str]:
    # 1. Environment variable path
    env_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # 2. Check standard filenames in project paths
    candidate_names = [
        "firebase-credentials.json",
        "serviceAccountKey.json",
        "firebase_key.json",
        "firebase-adminsdk.json"
    ]
    search_dirs = [BASE_DIR, ROOT_DIR, os.path.join(ROOT_DIR, "backend")]
    for d in search_dirs:
        for name in candidate_names:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
    return None

def init_firebase():
    global _firestore_client, _db_mode
    if _firestore_client is not None:
        return _firestore_client

    if not FIREBASE_AVAILABLE:
        print("[Firebase] firebase-admin package not available. Using in-memory fallback store.")
        _db_mode = "local_memory"
        return None

    # Check for direct JSON in environment variable
    raw_env_key = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY")
    cred = None

    if raw_env_key:
        try:
            cert_dict = json.loads(raw_env_key)
            cred = credentials.Certificate(cert_dict)
        except Exception as e:
            print(f"[Firebase] Error parsing FIREBASE_SERVICE_ACCOUNT_KEY env var: {e}")

    # Check for credentials JSON file
    if not cred:
        key_path = _find_service_account_path()
        if key_path:
            try:
                cred = credentials.Certificate(key_path)
                print(f"[Firebase] Loaded service account key from {key_path}")
            except Exception as e:
                print(f"[Firebase] Error loading key file {key_path}: {e}")

    # Attempt to initialize
    try:
        if cred:
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.get_app()
            _firestore_client = firestore.client()
            _db_mode = "firestore"
            print("[Firebase] Cloud Firestore successfully initialized.")
            return _firestore_client
        else:
            # Check if default Google Application Credentials exist (e.g., Cloud Run / App Engine)
            if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("GCLOUD_PROJECT"):
                if not firebase_admin._apps:
                    firebase_admin.initialize_app()
                _firestore_client = firestore.client()
                _db_mode = "firestore"
                print("[Firebase] Cloud Firestore initialized via Google Application Default Credentials.")
                return _firestore_client
    except Exception as e:
        print(f"[Firebase] Firestore initialization failed: {e}")

    print("[Firebase] No credentials found. Operating in local memory mode (ready for Firebase credentials).")
    _db_mode = "local_memory"
    return None

def is_db_connected() -> bool:
    return _db_mode in ("firestore", "local_memory")

def get_db_mode() -> str:
    return _db_mode

def get_db_connection():
    """Compatibility stub for previous SQLite connection."""
    return None

# ==================== DATA ACCESS LAYER (FIRESTORE / FALLBACK) ====================

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    if not email:
        return None
    clean_email = email.strip().lower()
    
    if _db_mode == "firestore" and _firestore_client:
        try:
            users_ref = _firestore_client.collection("users")
            query = users_ref.where("email", "==", clean_email).limit(1).stream()
            for doc in query:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            return None
        except Exception as e:
            print(f"[Firebase] Error in get_user_by_email: {e}")

    # Fallback to local store
    for doc_id, user in _local_db["users"].items():
        if user.get("email") == clean_email:
            res = dict(user)
            res["id"] = doc_id
            return res
    return None

def get_user_by_id(user_id: Any) -> Optional[Dict[str, Any]]:
    if not user_id:
        return None
    str_id = str(user_id)

    if _db_mode == "firestore" and _firestore_client:
        try:
            doc = _firestore_client.collection("users").document(str_id).get()
            if doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            return None
        except Exception as e:
            print(f"[Firebase] Error in get_user_by_id: {e}")

    # Fallback to local store
    user = _local_db["users"].get(str_id)
    if user:
        res = dict(user)
        res["id"] = str_id
        return res
    return None

def create_user(name: str, email: str, password_hash: str) -> Dict[str, Any]:
    clean_name = name.strip()
    clean_email = email.strip().lower()
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    user_data = {
        "name": clean_name,
        "email": clean_email,
        "password_hash": password_hash,
        "created_at": created_at
    }

    if _db_mode == "firestore" and _firestore_client:
        try:
            doc_ref = _firestore_client.collection("users").document()
            user_data["id"] = doc_ref.id
            doc_ref.set(user_data)
            return user_data
        except Exception as e:
            print(f"[Firebase] Error creating user in Firestore: {e}")

    # Fallback to local store
    new_id = str(uuid.uuid4())[:8]
    user_data["id"] = new_id
    _local_db["users"][new_id] = user_data
    return user_data

def create_planning_history(
    user_id: Any,
    planner_type: str,
    title: str,
    budget: float,
    estimated_cost: float,
    remaining: float,
    status: str,
    inputs_json: str,
    recommendations_json: str,
    created_at: Optional[str] = None
) -> str:
    if not created_at:
        created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    history_data = {
        "user_id": str(user_id),
        "planner_type": planner_type,
        "title": title,
        "budget": float(budget),
        "estimated_cost": float(estimated_cost),
        "remaining": float(remaining),
        "status": status,
        "inputs_json": inputs_json if isinstance(inputs_json, str) else json.dumps(inputs_json),
        "recommendations_json": recommendations_json if isinstance(recommendations_json, str) else json.dumps(recommendations_json),
        "created_at": created_at
    }

    if _db_mode == "firestore" and _firestore_client:
        try:
            doc_ref = _firestore_client.collection("planning_history").document()
            history_data["id"] = doc_ref.id
            doc_ref.set(history_data)
            return doc_ref.id
        except Exception as e:
            print(f"[Firebase] Error creating planning history in Firestore: {e}")

    # Fallback to local store
    new_id = str(uuid.uuid4())[:8]
    history_data["id"] = new_id
    _local_db["planning_history"][new_id] = history_data
    return new_id

def get_user_planning_history(user_id: Any, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    str_user_id = str(user_id)

    if _db_mode == "firestore" and _firestore_client:
        try:
            ref = _firestore_client.collection("planning_history")
            query = ref.where("user_id", "==", str_user_id).order_by("created_at", direction=firestore.Query.DESCENDING)
            if limit:
                query = query.limit(limit)
            docs = query.stream()
            results = []
            for doc in docs:
                item = doc.to_dict()
                item["id"] = doc.id
                results.append(item)
            return results
        except Exception as e:
            print(f"[Firebase] Error querying planning history: {e}")

    # Fallback to local store
    matched = [
        item for item in _local_db["planning_history"].values()
        if str(item.get("user_id")) == str_user_id
    ]
    matched.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
    if limit:
        matched = matched[:limit]
    return matched

def get_planning_history_by_id(history_id: Any, user_id: Optional[Any] = None) -> Optional[Dict[str, Any]]:
    str_id = str(history_id)
    str_user_id = str(user_id) if user_id is not None else None

    if _db_mode == "firestore" and _firestore_client:
        try:
            doc = _firestore_client.collection("planning_history").document(str_id).get()
            if doc.exists:
                item = doc.to_dict()
                item["id"] = doc.id
                if str_user_id is None or str(item.get("user_id")) == str_user_id:
                    return item
            return None
        except Exception as e:
            print(f"[Firebase] Error fetching history record: {e}")

    # Fallback to local store
    item = _local_db["planning_history"].get(str_id)
    if item:
        if str_user_id is None or str(item.get("user_id")) == str_user_id:
            res = dict(item)
            res["id"] = str_id
            return res
    return None

def delete_planning_history(history_id: Any, user_id: Any) -> bool:
    str_id = str(history_id)
    str_user_id = str(user_id)

    if _db_mode == "firestore" and _firestore_client:
        try:
            doc_ref = _firestore_client.collection("planning_history").document(str_id)
            doc = doc_ref.get()
            if doc.exists and str(doc.to_dict().get("user_id")) == str_user_id:
                doc_ref.delete()
                return True
            return False
        except Exception as e:
            print(f"[Firebase] Error deleting history item: {e}")

    # Fallback to local store
    item = _local_db["planning_history"].get(str_id)
    if item and str(item.get("user_id")) == str_user_id:
        del _local_db["planning_history"][str_id]
        return True
    return False

def get_user_stats(user_id: Any) -> Dict[str, Any]:
    history = get_user_planning_history(user_id)
    total_plans = len(history)
    total_budgeted = sum(float(h.get("budget", 0)) for h in history)
    total_saved = sum(float(h.get("remaining", 0)) for h in history)
    return {
        "total_plans": total_plans,
        "total_budgeted": total_budgeted,
        "total_saved": total_saved
    }

# ==================== INITIALIZATION & SEEDING ====================

def init_db():
    init_firebase()
    
    # Check if demo user exists
    demo_email = "demo@pocketsmart.ai"
    demo_user = get_user_by_email(demo_email)

    if not demo_user:
        demo_pwd_hash = hash_password("demo1234")
        demo_user = create_user("Alex Johnson", demo_email, demo_pwd_hash)
        demo_user_id = demo_user["id"]

        # Insert realistic sample history records
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

        create_planning_history(
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
        )

        create_planning_history(
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
        )
        print("[Firebase] Seeded demo user and realistic initial history.")

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
