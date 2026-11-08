import os
import sys
from pathlib import Path

# Add project root to sys.path so running directly via VS Code / python main.py always works
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.core.config import settings, FRONTEND_DIR
from backend.app.streaming.kafka_producer import streamer
from backend.app.api.v1.router import api_v1_router
from backend.app.api.websockets.feed import router as ws_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-start transaction streaming simulator on startup
    streamer.start()
    yield
    # Gracefully stop streamer on shutdown
    streamer.stop()
    if streamer._task:
        try:
            await streamer._task
        except (asyncio.CancelledError, Exception):
            pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_TAGLINE,
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware for local and cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(("/css", "/js", "/static")) or request.url.path in ["/", "/index.html", "/login.html"]:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Mount API Routers (both /api/v1 and legacy /api paths)
app.include_router(api_v1_router, prefix=settings.API_V1_STR)
app.include_router(api_v1_router, prefix=settings.API_LEGACY_STR)

# Mount Real-Time WebSocket Feeds
app.include_router(ws_router)

# Mount Frontend static assets and serve dashboard
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    if (FRONTEND_DIR / "css").exists():
        app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    if (FRONTEND_DIR / "js").exists():
        app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(
                index_file,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"}
            )
        return {"message": "ShieldPlus AI Backend is running. Frontend index.html is being initialized."}

    @app.get("/login", include_in_schema=False)
    @app.get("/login.html", include_in_schema=False)
    async def serve_login():
        login_file = FRONTEND_DIR / "login.html"
        if login_file.exists():
            return FileResponse(
                login_file,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"}
            )
        return FileResponse(FRONTEND_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=[str(ROOT_DIR / "backend")],
        reload_excludes=["*.db", "*.db-journal", "*.db-wal", "*.log"],
    )
