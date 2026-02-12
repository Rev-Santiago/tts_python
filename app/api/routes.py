"""
API routes for TTS synthesis
"""
import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas import TTSRequest
from app.core.lexicon import apply_custom_phonetics
from app.core.tts_engine import PiperEngine
from app.core.qwen3_engine import Qwen3Engine
from app.config import settings


logger = logging.getLogger(__name__)
router = APIRouter()


def create_tts_engine():
    """Factory function to create TTS engine based on configuration"""
    if settings.TTS_ENGINE == "qwen3":
        logger.info(f"Using Qwen3-TTS engine: {settings.QWEN3_SERVER_URL}")
        return Qwen3Engine(
            server_url=settings.QWEN3_SERVER_URL
        )
    else:
        logger.info("Using Piper TTS engine")
        return PiperEngine()


@router.post("/v1/synthesis")
async def synthesize_audio(request: TTSRequest):
    """
    Simple synchronous TTS endpoint (for testing)
    Returns a complete WAV file
    """
    print("Hello")
    engine = create_tts_engine()
    print("Done Create engine")

    # Apply Tagalog phonetic fixes before synthesis
    processed_text = apply_custom_phonetics(request.text)
    
    # Collect all audio chunks
    audio_chunks = []
    async for msg_type, data in engine.synthesize_stream(
        text=processed_text, # Use the improved text
        speaker_id=request.speaker_id,
        length_scale=1.0 / request.speed
    ):
        print(data)

        if msg_type == "audio":
            audio_chunks.append(data)
        elif msg_type == "error":
            raise HTTPException(status_code=500, detail=data.get("message", "TTS error"))
    
    # Combine all audio
    complete_audio = b''.join(audio_chunks)
    
    # Create WAV header
    wav_data = _create_wav(complete_audio, settings.SAMPLE_RATE)
    
    return StreamingResponse(
        iter([wav_data]),
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=speech.wav"}
    )


@router.websocket("/ws/generate")
async def websocket_tts_stream(websocket: WebSocket):
    """
    WebSocket endpoint for streaming TTS with viseme synchronization
    
    Protocol:
    1. Client sends JSON: {"text": "...", "speaker_id": 0, "speed": 1.0}
    2. Server streams:
       - Binary frames: Raw 16-bit PCM audio chunks
       - Text frames: JSON viseme events
    3. Server sends final text frame: {"type": "complete"}
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        # Receive request
        data = await websocket.receive_text()
        request_data = json.loads(data)
        
        text = request_data.get('text', '')
        speaker_id = request_data.get('speaker_id', 0)
        speed = request_data.get('speed', 1.0)
        voice_id = request_data.get('voice_id')
        
        if not text:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Text is required"
            }))
            await websocket.close()
            return
        
        logger.info(f"Generating TTS for: {text[:50]}... (speaker: {speaker_id})")
        
        # Initialize engine based on configuration
        engine = create_tts_engine()
        
        # Stream results
        async for msg_type, data in engine.synthesize_stream(
            text=text,
            speaker_id=speaker_id,
            length_scale=1.0 / speed
        ):
            if msg_type == "audio":
                # Send binary audio chunk
                await websocket.send_bytes(data)
                
            elif msg_type == "viseme":
                # Send viseme event as JSON text
                await websocket.send_text(json.dumps(data))
                
            elif msg_type == "complete":
                # Send completion marker
                await websocket.send_text(json.dumps({"type": "complete"}))
                
            elif msg_type == "error":
                # Send error and close
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": data.get("message", "Unknown error")
                }))
                break
        
        logger.info("TTS generation complete")
        
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e)
            }))
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


def _create_wav(pcm_data: bytes, sample_rate: int = 22050) -> bytes:
    """Create a WAV file from raw PCM data"""
    import io
    import wave
    
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    
    return wav_buffer.getvalue()
