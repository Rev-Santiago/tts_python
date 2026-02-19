import httpx
import time
import wave
import io

def test_chat_stream():
    url = "http://localhost:8010/api/v1/chat"
    payload = {
        "text": "Explain why the sky is blue in one short sentence.",
        "speaker_id": 0,
        "speed": 1.0
    }

    print(f"🚀 Sending request to {url}...")
    start_time = time.time()
    
    # Collect raw PCM audio chunks
    raw_audio = bytearray()
    first_chunk_time = None
    
    try:
        with httpx.stream("POST", url, json=payload, timeout=None) as response:
            if response.status_code != 200:
                print(f"❌ Error {response.status_code}: {response.read().decode()}")
                return

            print("⏳ Receiving audio stream...")
            
            for chunk in response.iter_bytes():
                if chunk:
                    if first_chunk_time is None:
                        first_chunk_time = time.time() - start_time
                        print(f"✅ First audio received in: {first_chunk_time:.2f}s")
                    
                    raw_audio.extend(chunk)
                    print(".", end="", flush=True)

    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        return

    # SAVE AS VALID WAV
    output_file = "stream_test.wav"
    try:
        with wave.open(output_file, "wb") as wav_file:
            wav_file.setnchannels(1)       # Mono
            wav_file.setsampwidth(2)       # 16-bit
            wav_file.setframerate(22050)   # 22.05kHz (Standard for Piper/Qwen)
            wav_file.writeframes(raw_audio)
            
        print(f"\n\n💾 Valid WAV saved to: {output_file}")
        print("▶️  You can now play this file in Media Player!")
        
    except Exception as e:
        print(f"Error saving WAV: {e}")

if __name__ == "__main__":
    test_chat_stream()