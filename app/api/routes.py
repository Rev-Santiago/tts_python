"""
API routes for TTS synthesis
"""
import logging
import json
import re
import traceback
import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse
from app.api.schemas import TTSRequest
from app.config import settings
from app.service.tts_service import generate_tts_audio, create_tts_engine

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/v1/chat")
async def chat_with_audio(request: TTSRequest):
    """
    Optimized Chat Endpoint with Look-Ahead Buffering:
    1. Streams text from Ollama (low latency).
    2. Buffers at least two sentences to provide TTS context (better intonation).
    3. Streams audio bytes sentence-by-sentence.
    """
    async def response_generator():
        ollama_url = "http://localhost:11434/api/generate"
        ollama_req = {
            "model": "gemma3:4b", 
            "prompt": request.text, 
            "stream": True 
        }

        print(f"DEBUG: Starting stream for prompt: {request.text[:30]}...")
        
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", ollama_url, json=ollama_req) as response:
                    buffer = ""
                    sentence_queue = [] # Queue to hold pending sentences
                    sentence_endings = re.compile(r'(?<=[.?!])\s+|(?<=\n)')

                    async for chunk in response.aiter_bytes():
                        if not chunk: continue
                        
                        try:
                            data = json.loads(chunk.decode("utf-8"))
                            token = data.get("response", "")
                            buffer += token
                            
                            # Split buffer into sentences
                            parts = sentence_endings.split(buffer)
                            
                            if len(parts) > 1:
                                # Add complete sentences to the queue
                                for i in range(len(parts) - 1):
                                    sentence_queue.append(parts[i].strip())
                                # Keep the trailing fragment in the buffer
                                buffer = parts[-1]

                                # LOOK-AHEAD: Only process if we have at least 2 sentences
                                # This ensures the engine has context for the next thought
                                while len(sentence_queue) > 1:
                                    current_speech = sentence_queue.pop(0)
                                    if current_speech:
                                        print(f"DEBUG: Speaking (buffered): {current_speech[:30]}...")
                                        async for msg_type, audio_data in generate_tts_audio(
                                            current_speech, request.voice, request.speed
                                        ):
                                            if msg_type == "audio":
                                                yield audio_data

                        except json.JSONDecodeError:
                            continue
                    
                    # Final cleanup: Process everything left in the queue and buffer
                    if buffer.strip():
                        sentence_queue.append(buffer.strip())
                    
                    for remaining_speech in sentence_queue:
                        if remaining_speech:
                            print(f"DEBUG: Speaking (final): {remaining_speech[:30]}...")
                            async for msg_type, audio_data in generate_tts_audio(
                                remaining_speech, request.voice, request.speed
                            ):
                                if msg_type == "audio":
                                    yield audio_data

        except Exception as e:
            logger.error(f"Stream error: {e}")
            print(traceback.format_exc())

    return StreamingResponse(response_generator(), media_type="audio/wav")


@router.post("/v1/synthesis")
async def synthesize_audio(request: TTSRequest):
    audio_chunks = []
    
    # Use the service function
    async for msg_type, data in generate_tts_audio(
        text=request.text, 
        voice=request.voice, 
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
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        data = await websocket.receive_text()
        request_data = json.loads(data)
        
        text = request_data.get('text', '')
        speaker_id = request_data.get('speaker_id', 0)
        speed = request_data.get('speed', 1.0)
        
        if not text:
            await websocket.send_text(json.dumps({"type": "error", "message": "Text is required"}))
            await websocket.close()
            return
        
        logger.info(f"Generating TTS for: {text[:50]}... (speaker: {speaker_id})")
        
        async for msg_type, data in generate_tts_audio(text, speaker_id, speed):
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
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


def _create_wav(pcm_data: bytes, sample_rate: int = 22050) -> bytes:
    import io
    import wave
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    return wav_buffer.getvalue()