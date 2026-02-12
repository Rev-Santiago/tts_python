"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional


class TTSRequest(BaseModel):
    """Request schema for TTS synthesis"""
    text: str = Field(..., description="Text to synthesize", min_length=1, max_length=5000)
    voice_id: Optional[str] = Field(None, description="Voice model ID (e.g., 'en_US-libritts-high')")
    speaker_id: int = Field(0, description="Speaker ID for multi-speaker models (0=female, 1=male typically)")
    speed: float = Field(1.0, description="Speech speed multiplier (1.0=normal, 0.5=half speed, 2.0=double)", ge=0.5, le=2.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, this is a test of the text to speech system.",
                "voice_id": "en_US-libritts-high",
                "speaker_id": 0,
                "speed": 1.0
            }
        }


class VisemeEvent(BaseModel):
    """Schema for viseme event data"""
    type: str = "viseme_event"
    offset_ms: int = Field(..., description="Time offset in milliseconds from stream start")
    duration_ms: int = Field(..., description="Duration of the viseme in milliseconds")
    phoneme: str = Field(..., description="Original phoneme")
    viseme_id: int = Field(..., description="Viseme ID (0-20)")
    viseme_name: str = Field(..., description="Human-readable viseme name")


class StreamComplete(BaseModel):
    """Completion marker for stream"""
    type: str = "complete"
    total_duration_ms: Optional[int] = None
