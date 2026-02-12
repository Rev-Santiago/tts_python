"""
Configuration settings for the TTS server
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # TTS Engine Selection
    TTS_ENGINE: str = "qwen3"  # "piper" or "qwen3"
    
    # Model settings (Piper)
    MODELS_DIR: Path = Path(__file__).parent.parent / "models"
    DEFAULT_VOICE: str = "en_US-libritts-high"
    
    # Audio settings
    SAMPLE_RATE: int = 22050
    CHUNK_SIZE: int = 2048  # Audio chunk size in bytes
    
    # Piper settings
    PIPER_EXECUTABLE: str = "piper"  # Assumes piper is in PATH
    
    # Qwen3-TTS settings
    QWEN3_SERVER_URL: str = "http://192.168.3.100:8880"
    QWEN3_VOICE: str = "Vivian"  # Default voice
    QWEN3_LANGUAGE: str = "Auto"  # Auto-detect or specify language
    QWEN3_FORMAT: str = "pcm"  # pcm, mp3, wav, opus, aac, flac
    
    # Hybrid Mode (use Piper for visemes even with Qwen3 audio)
    HYBRID_MODE: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
