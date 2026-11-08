"""
Security, Authentication & Token Management
Cryptographic password hashing and token generation using Python standard library.
"""
import hashlib
import secrets
import base64
import json
import time
from typing import Optional, Dict, Any

SECRET_KEY = "shieldplus_finsecure_supersecret_production_key_2026"

def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with a cryptographically secure random salt.
    Format: <salt>$<hash>
    """
    if not password:
        password = ""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}${key.hex()}"

def verify_password(stored_hash: str, password: str) -> bool:
    """
    Verifies a plaintext password against the stored salt$hash string using constant-time comparison.
    Also supports fallback matching for backward compatibility.
    """
    if not stored_hash or not password:
        return False
    try:
        if '$' in stored_hash:
            salt, key_hex = stored_hash.split('$', 1)
            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return secrets.compare_digest(new_key.hex(), key_hex)
        else:
            # Fallback for plain SHA256 or raw string
            raw_sha = hashlib.sha256(password.encode('utf-8')).hexdigest()
            return secrets.compare_digest(stored_hash, raw_sha) or secrets.compare_digest(stored_hash, password)
    except Exception:
        return False

def generate_auth_token(user_id: int, email: str, role: str = "Admin") -> str:
    """
    Generates a tamper-proof cryptographic session token.
    Format: base64(payload).signature
    """
    payload = {
        "uid": user_id,
        "email": email,
        "role": role,
        "exp": int(time.time()) + (24 * 3600), # 24 hours validity
        "nonce": secrets.token_hex(8)
    }
    payload_json = json.dumps(payload, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode('utf-8')).decode('utf-8').rstrip('=')
    
    sig = hashlib.sha256(f"{payload_b64}.{SECRET_KEY}".encode('utf-8')).hexdigest()[:32]
    return f"sp_{payload_b64}.{sig}"

def verify_auth_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validates the token signature and expiration, returning the payload if valid.
    """
    if not token or not token.startswith("sp_"):
        return None
    try:
        clean = token[3:]
        if '.' not in clean:
            return None
        payload_b64, sig = clean.split('.', 1)
        
        # Verify signature
        expected_sig = hashlib.sha256(f"{payload_b64}.{SECRET_KEY}".encode('utf-8')).hexdigest()[:32]
        if not secrets.compare_digest(sig, expected_sig):
            return None
        
        # Decode payload (re-pad base64 if needed)
        padding = '=' * (4 - (len(payload_b64) % 4)) if len(payload_b64) % 4 != 0 else ''
        payload_json = base64.urlsafe_b64decode(payload_b64 + padding).decode('utf-8')
        payload = json.loads(payload_json)
        
        # Check expiration
        if payload.get("exp", 0) < time.time():
            return None
        
        return payload
    except Exception:
        return None
