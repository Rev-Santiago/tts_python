import logging
from app.core.tts_engine import PiperEngine
from app.core.qwen3_engine import Qwen3Engine
from app.config import settings

logger = logging.getLogger(__name__)

def create_tts_engine():
    """Factory function to create TTS engine based on configuration"""
    if settings.TTS_ENGINE == "qwen3":
        logger.info(f"Using Qwen3-TTS engine: {settings.QWEN3_SERVER_URL}")
        return Qwen3Engine(server_url=settings.QWEN3_SERVER_URL)
    else:
        logger.info("Using Piper TTS engine")
        return PiperEngine()

async def generate_tts_audio(text: str, speaker_id: int = 0, speed: float = 1.0):
    """
    Core business logic for generating TTS audio chunks.
    This function is reusable across different endpoints.
    """
    engine = create_tts_engine()
    
    # Piper length_scale is the inverse of speed
    length_scale = 1.0 / speed
    
    async for msg_type, data in engine.synthesize_stream(
        text=text,
        speaker_id=speaker_id,
        length_scale=length_scale
    ):
        yield msg_type, data