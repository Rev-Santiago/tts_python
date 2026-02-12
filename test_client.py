"""
Simple Python client to test the TTS WebSocket streaming
"""
import asyncio
import websockets
import json
import wave
import sys


async def test_tts_stream(text: str, output_file: str = "output.wav"):
    """
    Test the TTS WebSocket endpoint and save audio to file
    
    Args:
        text: Text to synthesize
        output_file: Output WAV file path
    """
    uri = "ws://localhost:8000/api/ws/generate"
    
    print(f"Connecting to {uri}...")
    
    audio_chunks = []
    viseme_events = []
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Send request
            request = {
                "text": text,
                "speaker_id": 0,
                "speed": 1.0
            }
            
            print(f"Sending request: {text}")
            await websocket.send(json.dumps(request))
            
            # Receive stream
            print("Receiving stream...")
            
            async for message in websocket:
                if isinstance(message, bytes):
                    # Binary audio chunk
                    audio_chunks.append(message)
                    print(f"  Audio chunk: {len(message)} bytes")
                    
                else:
                    # JSON message
                    data = json.loads(message)
                    
                    if data['type'] == 'viseme_event':
                        viseme_events.append(data)
                        print(f"  Viseme: {data['viseme_name']:>3} (ID: {data['viseme_id']:>2}) "
                              f"at {data['offset_ms']:>5}ms for {data['duration_ms']:>3}ms - "
                              f"phoneme: '{data['phoneme']}'")
                    
                    elif data['type'] == 'complete':
                        print("\n✅ Stream complete!")
                        break
                    
                    elif data['type'] == 'error':
                        print(f"\n❌ Error: {data['message']}")
                        return
            
            # Save audio to WAV file
            if audio_chunks:
                complete_audio = b''.join(audio_chunks)
                
                with wave.open(output_file, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(22050)  # 22050 Hz
                    wav_file.writeframes(complete_audio)
                
                print(f"\n💾 Saved audio to: {output_file}")
                print(f"   Audio duration: ~{len(complete_audio) / (2 * 22050):.2f} seconds")
                print(f"   Total viseme events: {len(viseme_events)}")
            else:
                print("\n⚠️  No audio received!")
                
    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ WebSocket error: {e}")
        print("   Make sure the server is running: python -m app.main")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "Hello world! This is a test of the offline text to speech system with viseme synchronization."
    
    print("=" * 80)
    print("TTS WebSocket Client Test")
    print("=" * 80)
    print()
    
    asyncio.run(test_tts_stream(text))
    
    print()
    print("=" * 80)
