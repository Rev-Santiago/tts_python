"""
API routes for TTS synthesis
"""
import logging
import json
import traceback
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse
from app.api.schemas import TTSRequest
from app.config import settings
from app.service.tts_service import generate_tts_audio, create_tts_engine


logger = logging.getLogger(__name__)
router = APIRouter()

import httpx

@router.post("/v1/chat")
async def chat_with_audio(request: TTSRequest):
    """
    1. Sends user text to Ollama (Gemma 3)
    2. Takes LLM response and pipes it to the TTS Service for audio generation
    """
    # 1. Process request via Ollama
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            ollama_res = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma3:4b", # Or gemma3:7b / 12b based on your specs
                    "prompt": request.text, 
                    "stream": False
                }
            )
            llm_text = ollama_res.json().get("response", "")
            
        if not llm_text:
            raise HTTPException(status_code=500, detail="LLM failed to generate a response")

        # 2. Generate audio from the LLM text using your new service
        audio_chunks = []
        async for msg_type, data in generate_tts_audio(llm_text, request.speaker_id, request.speed):
            if msg_type == "audio":
                audio_chunks.append(data)
            elif msg_type == "error":
                 raise HTTPException(status_code=500, detail="TTS Service error")
        
        complete_audio = b''.join(audio_chunks)
        wav_data = _create_wav(complete_audio, settings.SAMPLE_RATE)
        
        return StreamingResponse(
            iter([wav_data]), 
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=chat_response.wav"}
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/v1/synthesis")
async def synthesize_audio(request: TTSRequest):
    audio_chunks = []
    
    # Use the service function
    async for msg_type, data in generate_tts_audio(
        text=request.text, 
        speaker_id=request.speaker_id, 
        speed=request.speed
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
#        async for msg_type, data in engine.synthesize_stream(
#            text=text,
#            speaker_id=speaker_id,
#            length_scale=1.0 / speed
#        ):
        async for msg_type, data in generate_tts_audio(text, speaker_id, speed):
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
