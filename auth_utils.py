import os
import time
import json
import base64
import hmac
import hashlib
from typing import Optional, Dict, Any

SECRET_KEY = os.environ.get("SESSION_SECRET", "pocketsmart-jwt-secret-key-prod-9921")

def create_jwt_token(payload: Dict[str, Any], expires_in: int = 86400 * 7) -> str:
    """Creates a signed HS256 JWT token using standard Python libraries."""
    header = {"alg": "HS256", "typ": "JWT"}
    header_bytes = json.dumps(header, separators=(',', ':')).encode('utf-8')
    header_b64 = base64.urlsafe_b64encode(header_bytes).decode('utf-8').rstrip('=')

    p = dict(payload)
    p["iat"] = int(time.time())
    p["exp"] = int(time.time()) + expires_in
    payload_bytes = json.dumps(p, separators=(',', ':')).encode('utf-8')
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode('utf-8').rstrip('=')

    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')

    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies HS256 JWT token signature and expiry."""
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts

        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
        
        # Add padding to base64url
        padded_sig = sig_b64 + '=' * (-len(sig_b64) % 4)
        actual_sig = base64.urlsafe_b64decode(padded_sig.encode('utf-8'))

        if not hmac.compare_digest(actual_sig, expected_sig):
            return None

        padded_payload = payload_b64 + '=' * (-len(payload_b64) % 4)
        payload_data = json.loads(base64.urlsafe_b64decode(padded_payload.encode('utf-8')).decode('utf-8'))

        # Check expiration
        if payload_data.get("exp", 0) < time.time():
            return None

        return payload_data
    except Exception:
        return None
