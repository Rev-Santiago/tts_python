"""
Main FastAPI application
"""
import logging
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


# Create FastAPI app
app = FastAPI(
    title="Offline TTS Streaming Server",
    description="Text-to-Speech server with streaming audio and viseme synchronization for 3D animation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for local network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["TTS"])

# Serve static files (test client)
try:
    app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 80)
    logger.info("TTS Streaming Server Starting")
    logger.info(f"Host: {settings.HOST}:{settings.PORT}")
    logger.info(f"Models directory: {settings.MODELS_DIR}")
    logger.info(f"Default voice: {settings.DEFAULT_VOICE}")
    logger.info("=" * 80)
    
    # Check if models directory exists
    if not settings.MODELS_DIR.exists():
        logger.warning(f"Models directory does not exist: {settings.MODELS_DIR}")
        logger.warning("Please download Piper models and place them in the models/ directory")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("TTS Streaming Server Shutting Down")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TTS Streaming Server",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )
