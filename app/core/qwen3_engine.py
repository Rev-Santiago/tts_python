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
        voice: str = "vivian",
        length_scale: float = 1.0,
        response_format: str = "pcm",
        language: str = "Auto"
    ) -> AsyncGenerator[Tuple[str, Any], None]:
        """
        Generate speech using Qwen3-TTS server with true HTTP streaming.
        
        Args:
            text: Text to synthesize
            length_scale: Speech speed (inverse of speed parameter)
            voice: Voice name (Vivian, Eric, etc.)
            response_format: Audio format — use "pcm" for raw 16-bit PCM
            language: Language code or "Auto"
            
        Yields:
            ("audio", bytes) - Raw PCM audio data chunks
            ("complete", {}) - Completion signal
            ("error", {"message": str}) - Error message
        """
        try:
            # Convert length_scale (Piper convention) to speed (OpenAI convention)
            # length_scale=1.0 → speed=1.0, length_scale=0.9 → speed≈1.11 (faster)
            speed = 1.0 / length_scale if length_scale > 0 else 1.0
            speed = max(0.25, min(4.0, speed))

            request_data = {
                "input": text,
                "voice": voice,
                "model": "qwen3-tts",
                "response_format": response_format,  # "pcm" = raw 16-bit LE, 22050 Hz, mono
                "speed": speed,
                "stream": True,          # ← MUST be True for streaming
                "language": language,
            }

            # Use stream=True on the HTTP client so we get chunks as they arrive
            async with self.client.stream(
                "POST",
                f"{self.server_url}/v1/audio/speech",
                json=request_data,
                timeout=httpx.Timeout(connect=10.0, read=120.0, write=10.0, pool=5.0),
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    yield ("error", {"message": f"Qwen3-TTS error {response.status_code}: {body.decode(errors='replace')}"})
                    return

                # Stream raw audio bytes directly — no artificial sleep
                async for chunk in response.aiter_bytes(chunk_size=4096):
                    if chunk:
                        yield ("audio", chunk)

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