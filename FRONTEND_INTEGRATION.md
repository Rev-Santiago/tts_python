# 🎙️ Frontend Integration Guide: ReactJS & WebSockets
This document provides the technical specifications for connecting a ReactJS frontend to the TTS streaming server.

### 1. Connection Specifications

**WebSocket URL**: ws://192.168.3.119:8000/api/ws/generate

**Audio Format**: Raw 16-bit PCM (Mono)

**Sample Rate**: 22050 Hz

**Protocol**: Interleaved Binary (Audio) and JSON (Metadata)

### 2. Audio Scheduling Logic
Because the server streams audio in small chunks, calling source.start() immediately on every message will cause the audio to overlap or sound jumbled. You must manually queue the chunks using a nextStartTime reference.

#### Key Implementation Details:
- **Normalize Audio**: Incoming Int16 data must be divided by 32768.0 to convert it to Float32 for the Web Audio API.

- **Sequential Timing**: Each chunk's start time should be Math.max(nextStartTime, audioContext.currentTime).

- **Pointer Update**: After scheduling a chunk, update your reference: nextStartTime = startTime + buffer.duration.

### 3. Reference React Component
This component demonstrates the correct way to handle the WebSocket stream and audio queue.

```JavaScript
import React, { useState, useRef } from 'react';

const TTSIntegration = () => {
  const [status, setStatus] = useState('Ready');
  const audioCtx = useRef(null);
  const nextStartTime = useRef(0);

  const handleAudioChunk = (data) => {
    const ctx = audioCtx.current;
    const int16Array = new Int16Array(data);
    const float32Array = new Float32Array(int16Array.length);
    
    for (let i = 0; i < int16Array.length; i++) {
      float32Array[i] = int16Array[i] / 32768.0;
    }

    const buffer = ctx.createBuffer(1, float32Array.length, 22050);
    buffer.getChannelData(0).set(float32Array);
    
    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(ctx.destination);

    const startTime = Math.max(nextStartTime.current, ctx.currentTime);
    source.start(startTime);
    nextStartTime.current = startTime + buffer.duration;
  };

  const startStreaming = () => {
    if (!audioCtx.current) {
      audioCtx.current = new AudioContext({ sampleRate: 22050 });
    }
    
    nextStartTime.current = audioCtx.current.currentTime;
    const ws = new WebSocket("ws://192.168.3.119:8000/api/ws/generate");
    ws.binaryType = 'arraybuffer';

    ws.onopen = () => ws.send(JSON.stringify({ text: "Connection test successful.", speed: 1.0 }));
    ws.onmessage = (e) => {
      if (e.data instanceof ArrayBuffer) handleAudioChunk(e.data);
      else if (JSON.parse(e.data).type === 'complete') setStatus('Done');
    };
  };

  return <button onClick={startStreaming}>Test TTS Stream</button>;
};
```

### 4. Troubleshooting
**CORS Issues**: The backend is configured to allow all origins (allow_origins=["*"]).

**No Visemes**: When TTS_ENGINE is set to qwen3, only audio is sent. Switch to piper to test lip-sync viseme events.