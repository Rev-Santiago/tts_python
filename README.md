# Offline TTS Streaming Server

A high-performance, offline Text-to-Speech (TTS) streaming server. This system is designed to use **Qwen3-TTS** as the primary engine for high-quality speech synthesis, with **Piper TTS** available as a legacy/fallback option for viseme generation.

## Features

✅ **Qwen3-TTS Support** - High-quality, OpenAI-compatible synthesis (Default)  
✅ **Streaming Audio** - Low-latency PCM audio streaming via WebSocket  
✅ **Hybrid Mode** - Combine Qwen3 audio with Piper visemes for 3D lipsync  
✅ **Legacy Piper Support** - Use Piper TTS for purely local, lower-resource synthesis  
✅ **REST & WebSocket APIs** - Flexible integration options  

## Tech Stack

- **Backend**: FastAPI with async WebSocket support
- **Core Engine**: Qwen3-TTS (Remote or Local OpenAI-compatible server)
- **Legacy Engine**: Piper TTS (ONNX-based)
- **Audio Format**: 16-bit PCM, 22050 Hz, Mono

## Installation

### Prerequisites

- Python 3.9 or higher
- Access to a Qwen3-TTS server (e.g., running on another machine or port)

### Step 1: Install Dependencies

```bash
cd TTS_python
pip install -r requirements.txt
```

### Step 2: Configuration

Create a `.env` file in the root directory to configure your Qwen3 server:

```ini
# Server Settings
HOST=0.0.0.0
PORT=8000

# TTS Engine Selection
TTS_ENGINE=qwen3 

# Qwen3 Server Configuration
QWEN3_SERVER_URL=http://192.168.3.100:8880
QWEN3_VOICE=Vivian
```

## Usage

### Starting the Server

```bash
python -m app.main
```

The server will start on `http://0.0.0.0:8000`.

### Qwen3-TTS (Default)

The system is configured to use Qwen3-TTS by default. It expects an OpenAI-compatible TTS endpoint at the configured `QWEN3_SERVER_URL`.

**Pros:**
- Higher quality audio
- More natural prosody

**Cons:**
- Requires external server or GPU
- No native viseme support (unless using Hybrid Mode)

### Piper TTS (Legacy/Optional)

To use Piper TTS instead (e.g., for lower resource usage or native visemes):

1. Install Piper: `pip install piper-tts`
2. Download models: `python setup_models.py`
3. Set `TTS_ENGINE=piper` in your `.env` file.

**Pros:**
- Runs entirely on CPU
- Native viseme generation
- No external dependencies

**Cons:**
- Lower audio quality compared to Qwen3

## API Reference

### REST Endpoint

**POST** `/api/v1/synthesis`

Returns a complete WAV file.

```bash
curl -X POST "http://localhost:8000/api/v1/synthesis" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice_id": "Vivian"}' \
  --output speech.wav
```

### WebSocket Endpoint

**WS** `/api/ws/generate`

Real-time streaming audio.

**Client Send:**
```json
{
  "text": "Hello world",
  "voice_id": "Vivian",
  "speed": 1.0
}
```

**Server Sends:**
- **Binary frames**: Raw 16-bit PCM audio chunks
- **Text frames (JSON)**: `{"type": "complete"}`

## License

MIT License
