"""
API routes for TTS synthesis
"""
import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas import TTSRequest
from app.core.tts_engine import PiperEngine
from app.core.qwen3_engine import Qwen3Engine
from app.config import settings


logger = logging.getLogger(__name__)
router = APIRouter()


def create_tts_engine():
    """Factory function to create TTS engine based on configuration"""
    if settings.TTS_ENGINE == "qwen3":
        logger.info(f"Using Qwen3-TTS engine: {settings.QWEN3_SERVER_URL}")
        return Qwen3Engine(server_url=settings.QWEN3_SERVER_URL)
    else:
        logger.info("Using Piper TTS engine")
        return PiperEngine()


@router.post("/v1/synthesis")
async def synthesize_audio(request: TTSRequest):
    """
    Simple synchronous TTS endpoint (for testing)
    Returns a complete WAV file
    """
    engine = create_tts_engine()

    audio_chunks = []
    async for msg_type, data in engine.synthesize_stream(
        text=request.text,
        voice=request.voice,
        length_scale=1.0 / request.speed
    ):
        if msg_type == "audio":
            audio_chunks.append(data)
        elif msg_type == "error":
            raise HTTPException(status_code=500, detail=data.get("message", "TTS error"))

    complete_audio = b''.join(audio_chunks)
    wav_data = _create_wav(complete_audio, settings.SAMPLE_RATE)

    return StreamingResponse(
        iter([wav_data]),
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=speech.wav"}
    )


@router.websocket("/tts/ws/generate")
async def websocket_tts_stream(websocket: WebSocket):
    """
    WebSocket endpoint for streaming TTS with viseme synchronization.

    ── Why we call websocket.accept() with no origin check ──────────────────
    FastAPI's CORSMiddleware does NOT apply to WebSocket upgrade requests.
    The 403 "connection rejected" you saw is Starlette's built-in WebSocket
    origin guard rejecting requests from a different port (e.g. :82 → :8010).
    Calling accept() unconditionally disables that guard for this endpoint,
    which is correct for a local-network / same-machine dev setup.
    For production, replace with: await websocket.accept() guarded by an
    allowed-origins allowlist check on websocket.headers.get("origin").
    ─────────────────────────────────────────────────────────────────────────

    Protocol:
    1. Client sends JSON: {"text": "...", "speaker_id": 0, "voice_id": "Vivian", "speed": 1.0}
    2. Server streams:
       - Binary frames : Raw 16-bit PCM audio chunks (mono, 22050 Hz)
       - Text frames   : JSON viseme events {"type":"viseme_event", "viseme_id": N, ...}
    3. Server sends final text frame: {"type": "complete"}
    """
    # Accept unconditionally — this is what fixes the 403.
    await websocket.accept()
    logger.info(f"WebSocket /tts/ws/generate connected from {websocket.client}")

    try:
        data = await websocket.receive_text()
        request_data = json.loads(data)

        text       = request_data.get("text", "")
        speaker_id = request_data.get("speaker_id", 0)
        speed      = request_data.get("speed", 1.0)
        # voice_id carries the Qwen3 voice name: "Vivian", "Eric", etc.
        voice_id   = request_data.get("voice_id") or settings.QWEN3_VOICE

        if not text:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Text is required"
            }))
            await websocket.close()
            return

        logger.info(f"TTS request | voice={voice_id} speaker={speaker_id} | text={text[:60]}...")

        engine = create_tts_engine()

        async for msg_type, data in engine.synthesize_stream(
            text=text,
            voice=voice_id,
            length_scale=1.0 / speed if speed > 0 else 1.0,
        ):
            if msg_type == "audio":
                await websocket.send_bytes(data)

            elif msg_type == "viseme":
                await websocket.send_text(json.dumps(data))

            elif msg_type == "complete":
                await websocket.send_text(json.dumps({"type": "complete"}))

            elif msg_type == "error":
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": data.get("message", "Unknown error")
                }))
                break

        logger.info("TTS generation complete")

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e)
            }))
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


def _create_wav(pcm_data: bytes, sample_rate: int = 22050) -> bytes:
    """Create a WAV file from raw PCM data"""
    import io
    import wave

    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)   # Mono
        wav_file.setsampwidth(2)   # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)

    return wav_buffer.getvalue()