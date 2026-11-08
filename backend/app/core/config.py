import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent # backend/app
BACKEND_DIR = BASE_DIR.parent                     # backend
PROJECT_ROOT = BACKEND_DIR.parent                 # Root
DATA_DIR = PROJECT_ROOT / "data"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

DATA_DIR.mkdir(exist_ok=True)

# Safe loader for .env file without mandatory third-party dependency
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v
    except Exception:
        pass

class Settings(BaseModel):
    PROJECT_NAME: str = "ShieldPlus AI"
    PROJECT_TAGLINE: str = "Real-Time Autonomous Financial Fraud & Anomaly Intelligence Engine"
    API_V1_STR: str = "/api/v1"
    API_LEGACY_STR: str = "/api"
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
    
    # DB configuration
    DB_PATH: str = os.getenv("DB_PATH", str(DATA_DIR / "shieldplus.db"))
    
    # ML and Threshold Settings
    RISK_THRESHOLD_FLAG: float = 55.0     # Above 55 is flagged for investigation
    RISK_THRESHOLD_BLOCK: float = 78.0    # Above 78 is automatically blocked
    
    # Default Streaming settings
    DEFAULT_STREAM_RATE: float = 3.0      # Transactions per second
    ANOMALY_PROBABILITY: float = 0.12     # 12% baseline anomaly rate in simulation

    # Base Public Web Application URL (used for password reset links clickable on mobile & laptop)
    BASE_URL: str = os.getenv("BASE_URL", "http://127.0.0.1:8000")

    # Real SMTP Email Delivery Configuration
    # Supports Gmail (with App Password), Outlook, SendGrid, Brevo, AWS SES, or any standard SMTP server
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "ShieldPlus AI Security Core")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
    SMTP_USE_SSL: bool = os.getenv("SMTP_USE_SSL", "false").lower() in ("true", "1", "yes")

settings = Settings()
