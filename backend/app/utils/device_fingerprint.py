import hashlib

def generate_device_hash(user_agent: str, ip: str, hardware_token: str = "") -> str:
    raw = f"{user_agent}|{ip}|{hardware_token}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

