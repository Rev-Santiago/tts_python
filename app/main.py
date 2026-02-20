"""
Main FastAPI application
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# ── Lifespan (replaces deprecated on_event) ───────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 80)
    logger.info("TTS Streaming Server Starting")
    logger.info(f"Host: {settings.HOST}:{settings.PORT}")
    logger.info(f"Models directory: {settings.MODELS_DIR}")
    logger.info(f"Default voice: {settings.DEFAULT_VOICE}")
    logger.info(f"TTS Engine: {settings.TTS_ENGINE}")
    logger.info("=" * 80)

    if not settings.MODELS_DIR.exists():
        logger.warning(f"Models directory does not exist: {settings.MODELS_DIR}")

    yield

    # Shutdown
    logger.info("TTS Streaming Server Shutting Down")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Offline TTS Streaming Server",
    description="Text-to-Speech server with streaming audio and viseme synchronization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS — allow everything (local dev) ───────────────────────────────────────
# NOTE: CORSMiddleware does NOT cover WebSocket upgrades in FastAPI.
# WebSocket origin checking is handled inside the endpoint itself (see routes.py).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api", tags=["TTS"])

# ── Static files ──────────────────────────────────────────────────────────────
try:
    app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "TTS Streaming Server",
        "version": "1.0.0",
        "engine": settings.TTS_ENGINE,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info",
    )