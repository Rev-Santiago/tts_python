"""
Piper TTS Engine wrapper with streaming support
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional, Tuple
import struct

from app.config import settings
from app.core.viseme_map import VisemeMapper


logger = logging.getLogger(__name__)


class PiperEngine:
    """Wrapper for Piper TTS with streaming audio and phoneme alignment"""
    
    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize the Piper engine
        
        Args:
            model_path: Path to the .onnx model file
        """
        self.model_path = model_path or self._get_default_model()
        self.viseme_mapper = VisemeMapper()
        
    def _get_default_model(self) -> Path:
        """Get the default model path"""
        model_file = settings.MODELS_DIR / f"{settings.DEFAULT_VOICE}.onnx"
        if not model_file.exists():
            logger.warning(f"Model not found at {model_file}")
        return model_file
    
    async def synthesize_stream(
        self, 
        text: str, 
        voice: str | int = 0,
        length_scale: float = 1.0
    ) -> AsyncGenerator[Tuple[str, Any], None]:
        """
        Stream audio and viseme data from Piper
        
        Args:
            text: Text to synthesize
            speaker_id: Speaker ID (for multi-speaker models)
            length_scale: Speed control (1.0 = normal, <1 = faster, >1 = slower)
            
        Yields:
            Tuple of (message_type, data) where:
                - ("audio", bytes): Raw PCM audio chunk
                - ("viseme", dict): Viseme event with timing
                - ("complete", None): Stream finished
        """
        if not self.model_path.exists():
            logger.error(f"Model file not found: {self.model_path}")
            yield ("error", {"message": "Model file not found"})
            return
        
        # Build Piper command
        cmd = [
            settings.PIPER_EXECUTABLE,
            "--model", str(self.model_path),
            "--output-raw",  # Output raw PCM
            "--json-input",  # Accept JSON input for phoneme data
        ]
        
        # Create the process
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            logger.error(f"Piper executable not found: {settings.PIPER_EXECUTABLE}")
            yield ("error", {"message": "Piper executable not found. Please install piper-tts."})
            return
        
        # Prepare input JSON
        input_data = json.dumps({
            "text": text,
            "speaker_id": voice,
            "length_scale": length_scale,
            "output_file": "-",  # stdout
        })
        
        # Write input and close stdin
        if process.stdin is not None:
            process.stdin.write(input_data.encode('utf-8'))
            process.stdin.write(b'\n')
            await process.stdin.drain()
            process.stdin.close()
        else:
            logger.error("Piper process stdin is None - cannot send text for synthesis")
            yield ("error", {"message": "Internal process error: stdin not available"})
            return
        
        # Read outputs concurrently
        audio_task = asyncio.create_task(self._read_audio(process))
        phoneme_task = asyncio.create_task(self._read_phonemes(process))
        
        # Stream audio chunks
        audio_stream = await audio_task
        phoneme_data = await phoneme_task
        
        # Process phonemes into viseme events
        viseme_events = self._process_phonemes(phoneme_data)
        
        # Yield audio and visemes in synchronized manner
        audio_offset = 0
        viseme_idx = 0
        
        for chunk in audio_stream:
            # Calculate time offset for this chunk (assuming 16-bit PCM, mono, 22050 Hz)
            chunk_duration_ms = (len(chunk) / 2) / (settings.SAMPLE_RATE / 1000)
            
            # Yield any viseme events that occur during this chunk
            while viseme_idx < len(viseme_events):
                event = viseme_events[viseme_idx]
                if event['offset_ms'] <= audio_offset + chunk_duration_ms:
                    yield ("viseme", event)
                    viseme_idx += 1
                else:
                    break
            
            # Yield audio chunk
            yield ("audio", chunk)
            audio_offset += chunk_duration_ms
        
        # Yield any remaining viseme events
        while viseme_idx < len(viseme_events):
            yield ("viseme", viseme_events[viseme_idx])
            viseme_idx += 1
        
        # Signal completion
        yield ("complete", None)
        
        # Wait for process to finish
        await process.wait()
    
    async def _read_audio(self, process) -> list:
        """Read audio data from stdout"""
        chunks = []
        while True:
            chunk = await process.stdout.read(settings.CHUNK_SIZE)
            if not chunk:
                break
            chunks.append(chunk)
        return chunks
    
    async def _read_phonemes(self, process) -> Dict[str, Any]:
        """Read phoneme data from stderr (Piper outputs JSON alignment here)"""
        stderr_data = await process.stderr.read()
        stderr_text = stderr_data.decode('utf-8', errors='ignore')
        
        # Try to parse JSON from stderr
        # Piper may output multiple JSON objects or debug info
        phoneme_data = {"phonemes": []}
        
        for line in stderr_text.strip().split('\n'):
            if line.strip().startswith('{'):
                try:
                    data = json.loads(line)
                    if 'phonemes' in data:
                        phoneme_data = data
                        break
                except json.JSONDecodeError:
                    continue
        
        return phoneme_data
    
    def _process_phonemes(self, phoneme_data: Dict[str, Any]) -> list:
        """Convert phoneme timing data to viseme events"""
        events = []
        
        phonemes = phoneme_data.get('phonemes', [])
        for phon in phonemes:
            # Expected format: {"phoneme": "AO", "start": 0.1, "end": 0.2}
            phoneme = phon.get('phoneme', '')
            start_sec = phon.get('start', 0)
            end_sec = phon.get('end', 0)
            
            viseme_id = self.viseme_mapper.map_phoneme(phoneme)
            viseme_name = self.viseme_mapper.get_viseme_name(viseme_id)
            
            events.append({
                'type': 'viseme_event',
                'offset_ms': int(start_sec * 1000),
                'duration_ms': int((end_sec - start_sec) * 1000),
                'phoneme': phoneme,
                'viseme_id': viseme_id,
                'viseme_name': viseme_name,
            })
        
        return events
