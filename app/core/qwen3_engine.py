"""
Qwen3-TTS Engine Adapter
OpenAI-compatible TTS API client
"""
import httpx
import json
from typing import AsyncGenerator, Tuple, Any, Optional
from pathlib import Path
import asyncio

from .viseme_map import VisemeMapper


class Qwen3Engine:
    """
    Adapter for Qwen3-TTS server (OpenAI-compatible API)
    
    Note: Qwen3-TTS only provides audio output, not viseme data.
    For viseme generation, use hybrid mode with Piper.
    """
    
    def __init__(self, server_url: str = "http://192.168.3.100:8880"):
        self.server_url = server_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.viseme_mapper = VisemeMapper()
        
    async def synthesize_stream(
        self,
        text: str,
        length_scale: float = 1.0,
        voice: str = "vivian",
        response_format: str = "pcm",
        language: str = "Auto"
    ) -> AsyncGenerator[Tuple[str, Any], None]:
        """
        Generate speech using Qwen3-TTS server
        
        Args:
            text: Text to synthesize
            speaker_id: Not used (Qwen3 uses voice names instead)
            length_scale: Speech speed (inverse of speed parameter)
            voice: Voice name (Vivian, etc.)
            response_format: Audio format (pcm, mp3, wav, etc.)
            language: Language code or "Auto"
            
        Yields:
            ("audio", bytes) - Audio data chunks
            ("complete", {}) - Completion signal
            ("error", {"message": str}) - Error message
        """
        try:
            # Convert length_scale (Piper format) to speed (OpenAI format)
            speed = 1.0 / length_scale if length_scale > 0 else 1.0
            speed = max(0.25, min(4.0, speed))  # Clamp to valid range
            
            # Prepare request
            request_data = {
                "input": text,
                "task_type": "CustomVoice",
                "voice": voice,
                "model": "qwen3-tts",
                "response_format": response_format,
                "speed": speed,
                "stream": True,  # Use streaming for audio chunks
                "language": language
            }
            
            # Make request to Qwen3-TTS server
            response = await self.client.post(
                f"{self.server_url}/v1/audio/speech",
                json=request_data,
                timeout=60.0
            )
            
            if response.status_code != 200:
                error_msg = f"Qwen3-TTS error {response.status_code}: {response.text}"
                yield ("error", {"message": error_msg})
                return
            
            # Stream audio data in chunks
            audio_data = response.content
            
            # Send audio in chunks (similar to Piper behavior)
            chunk_size = 4096
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                yield ("audio", chunk)
                await asyncio.sleep(0.01)  # Small delay for streaming effect
            
            # Note: No viseme data available from Qwen3-TTS
            # Client should use hybrid mode with Piper for visemes
            
            # Send completion
            yield ("complete", {})
            
        except httpx.TimeoutException:
            yield ("error", {"message": "Qwen3-TTS server timeout"})
        except httpx.ConnectError:
            yield ("error", {"message": f"Cannot connect to Qwen3-TTS server at {self.server_url}"})
        except Exception as e:
            yield ("error", {"message": f"Qwen3-TTS error: {str(e)}"})
    
    async def get_available_voices(self) -> list:
        """Fetch available voices from Qwen3-TTS server"""
        try:
            response = await self.client.get(f"{self.server_url}/v1/voices")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            asyncio.create_task(self.close())
        except:
            pass
