"""
Interactive voice model downloader using Piper's built-in download system
"""
import sys
import subprocess
from pathlib import Path


MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

# Recommended voices with descriptions
RECOMMENDED_VOICES = {
    "1": {
        "name": "en_US-libritts-high",
        "description": "English US - High Quality - 903 speakers (Male & Female) - RECOMMENDED"
    },
    "2": {
        "name": "en_US-lessac-medium",
        "description": "English US - Lessac - Medium Quality (Female)"
    },
    "3": {
        "name": "en_US-ryan-high",
        "description": "English US - Ryan - High Quality (Male)"
    },
    "4": {
        "name": "en_US-amy-medium",
        "description": "English US - Amy - Medium Quality (Female)"
    },
}


def list_all_voices():
    """List all available voices using Piper"""
    print("\n" + "=" * 80)
    print("Fetching available voices from Piper...")
    print("=" * 80)
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "piper.download_voices"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("Error listing voices:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("Request timed out. Please check your connection.")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure piper-tts is installed: pip install piper-tts")


def download_voice(voice_name: str) -> bool:
    """
    Download a voice model using Piper's download system
    
    Args:
        voice_name: Voice identifier (e.g., 'en_US-lessac-medium')
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n[*] Downloading voice: {voice_name}")
    print(f"[*] Target directory: {MODELS_DIR}")
    print()
    
    try:
        # Run Piper's download command
        result = subprocess.run(
            [
                sys.executable, "-m", "piper.download_voices",
                voice_name,
                "--data-dir", str(MODELS_DIR)
            ],
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print(f"\n[OK] Successfully downloaded: {voice_name}")
            
            # Verify the model exists
            onnx_file = MODELS_DIR / f"{voice_name}.onnx"
            if onnx_file.exists():
                size_mb = onnx_file.stat().st_size / (1024 * 1024)
                print(f"[OK] Model file: {onnx_file.name} ({size_mb:.1f} MB)")
                return True
            else:
                print("[WARN] Model file not found after download")
                return False
        else:
            print(f"\n[FAIL] Download failed with exit code: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n[FAIL] Download timed out (>5 minutes)")
        return False
    except FileNotFoundError:
        print("\n[FAIL] Piper not found. Install with: pip install piper-tts")
        return False
    except Exception as e:
        print(f"\n[FAIL] Error during download: {e}")
        return False


def show_existing_models():
    """Show currently downloaded models"""
    onnx_files = list(MODELS_DIR.glob("*.onnx"))
    
    if onnx_files:
        print("\n[*] Currently installed models:")
        for model in onnx_files:
            size_mb = model.stat().st_size / (1024 * 1024)
            print(f"    - {model.name} ({size_mb:.1f} MB)")
        print()
    else:
        print("\n[*] No models currently installed")
        print()


def main():
    print("=" * 80)
    print("Piper TTS Voice Model Downloader")
    print("=" * 80)
    print("NOTE: This script is for downloading Piper TTS models only.")
    print("      Qwen3-TTS models are handled separately.")
    print("=" * 80)
    
    # Show existing models
    show_existing_models()
    
    # Show menu
    print("[*] Recommended voices:")
    for key, voice in RECOMMENDED_VOICES.items():
        print(f"    {key}. {voice['description']}")
    
    print("\n[*] Additional options:")
    print("    5. List all available voices")
    print("    6. Enter custom voice name")
    print("    7. Browse voices online")
    print("    q. Quit")
    print()
    
    # Get user choice
    choice = input("Select an option: ").strip()
    
    if choice.lower() == 'q':
        print("Goodbye!")
        return
    
    if choice == '5':
        list_all_voices()
        print("\nRun this script again to download a voice.")
        return
    
    if choice == '7':
        print("\n[*] Voice Browser:")
        print("    Visit: https://rhasspy.github.io/piper-samples")
        print("    You can listen to samples and find voice names there.")
        print("\nRun this script again to download a voice.")
        return
    
    if choice == '6':
        print("\n[*] Enter voice name (format: language-voice-quality)")
        print("    Example: en_US-lessac-medium")
        voice_name = input("Voice name: ").strip()
        
        if not voice_name:
            print("[FAIL] Invalid voice name")
            return
        
        success = download_voice(voice_name)
    
    elif choice in RECOMMENDED_VOICES:
        voice = RECOMMENDED_VOICES[choice]
        success = download_voice(voice['name'])
    
    else:
        print("[FAIL] Invalid choice!")
        return
    
    # Final summary
    print()
    print("=" * 80)
    if success:
        print("[SUCCESS] Voice model downloaded successfully!")
        print()
        print("Next steps:")
        print("  1. Start the server: python -m app.main")
        print("  2. Open browser: http://localhost:8000")
        print("  3. Or test with: python test_client.py")
    else:
        print("[FAILED] Model download unsuccessful")
        print()
        print("Troubleshooting:")
        print("  - Ensure piper-tts is installed: pip install piper-tts")
        print("  - Check your internet connection")
        print("  - Try a different voice")
    print("=" * 80)


if __name__ == "__main__":
    main()
