# Qwen3-TTS Integration Guide

## Overview

The TTS server now supports **dual-engine mode**: you can use either **Piper TTS** (local) or **Qwen3-TTS** (remote server).

## Configuration

Edit `.env` file or set environment variables:

```env
# Choose engine: "piper" or "qwen3"
TTS_ENGINE=qwen3

# Qwen3-TTS server settings
QWEN3_SERVER_URL=http://192.168.3.100:8880
QWEN3_VOICE=Vivian
QWEN3_LANGUAGE=Auto
QWEN3_FORMAT=pcm
```

## Usage

### Start Server with Qwen3

```powershell
# Set environment variable
$env:TTS_ENGINE="qwen3"

# Start server
python -m app.main
```

### Test Qwen3 Integration

```powershell
# REST API test
curl -X POST "http://localhost:8000/api/v1/synthesis" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from Qwen3","speaker_id":0}' \
  -o output.wav

# Or use the web client
# Open http://localhost:8000
```

## ⚠️ Important Limitation: No Viseme Support

**Qwen3-TTS does NOT provide phoneme/viseme timing data.**

This means:
- ✅ Audio generation works perfectly
- ❌ **No lip-sync data for 3D animations**
- ❌ Viseme events will NOT be sent to clients

### Impact on 3D Applications

If you're using this for 3D character lip-sync:

**Option 1: Use Piper** (Recommended for lip-sync)
```env
TTS_ENGINE=piper
```
- ✅ Full viseme support
- ✅ Real-time lip-sync data
- ⚠️ Requires Piper models downloaded

**Option 2: Hybrid Mode** (Future Feature)
```env
TTS_ENGINE=qwen3
HYBRID_MODE=true
```
- Would use Qwen3 for audio quality
- Would use Piper ONLY for viseme generation
- **(Not yet implemented)**

## API Compatibility

Both engines work with the same API:

### WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/generate');

ws.onopen = () => {
    ws.send(JSON.stringify({
        text: "Hello world",
        speaker_id: 0,  // Ignored by Qwen3
        speed: 1.0
    }));
};

ws.onmessage = (event) => {
    if (event.data instanceof Blob) {
        // Audio PCM data
    } else {
        const msg = JSON.parse(event.data);
        if (msg.type === 'viseme_event') {
            // Only with Piper engine!
            console.log('Viseme:', msg);
        }
    }
};
```

### REST API
```bash
POST /api/v1/synthesis
{
  "text": "Your text here",
  "speaker_id": 0,
  "speed": 1.0
}
```

## Qwen3-TTS Features

✅ **OpenAI-compatible API**  
✅ **Multi-language support** (10+ languages)  
✅ **Multiple voices** (Vivian, etc.)  
✅ **Multiple audio formats** (MP3, Opus, AAC, FLAC, WAV, PCM)  
✅ **Speed control** (0.25x to 4.0x)  
✅ **GPU-accelerated inference**  

## Available Qwen3 Voices

To see available voices:

```powershell
curl http://192.168.3.100:8880/v1/voices
```

Update `.env` with your preferred voice:
```env
QWEN3_VOICE=Vivian
```

## Troubleshooting

### "Cannot connect to Qwen3-TTS server"

1. **Check server is running:**
   ```powershell
   curl http://192.168.3.100:8880/health
   ```

2. **Verify network connectivity:**
   ```powershell
   ping 192.168.3.100
   ```

3. **Check firewall** on the Qwen3 server

### "No viseme events received"

This is expected! Qwen3-TTS doesn't provide viseme data.

**Solution:** Use `TTS_ENGINE=piper` if you need lip-sync.

### Switch back to Piper

```powershell
# Update .env
TTS_ENGINE=piper

# Restart server
python -m app.main
```

## Comparison

| Feature | Piper | Qwen3-TTS |
|---------|-------|-----------|
| **Setup** | Local models | Remote server |
| **Viseme Data** | ✅ Yes | ❌ No |
| **Lip-Sync** | ✅ Full support | ❌ Not supported |
| **Audio Quality** | Good | Possibly better |
| **Languages** | Many | 10+ |
| **Offline** | ✅ 100% | ⚠️ Needs network |
| **Speed** | Fast | Network dependent |
| **Installation** | Download models | Just config |

## Recommendation

**For 3D Lip-Sync Applications:** Use **Piper**  
**For Audio-Only Applications:** Either engine works  
**For Best Quality (no lip-sync needed):** Try **Qwen3-TTS**

---

**Created**: January 30, 2026  
**Server**: http://192.168.3.100:8880
