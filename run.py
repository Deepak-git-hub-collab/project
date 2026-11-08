import os
import sys
from pathlib import Path
import uvicorn

# Ensure repository root is on sys.path for backend package discovery
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

port = int(os.environ.get("PORT", 10000))

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port)
