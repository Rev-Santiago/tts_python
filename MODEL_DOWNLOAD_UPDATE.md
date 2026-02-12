# Model Download System Update

## What Changed

The model download system has been completely updated to use **Piper's official download API** instead of manual GitHub downloads.

## New Download Method

### Interactive Script (Recommended)
```powershell
python setup_models.py
```

Features:
- ✅ Menu of recommended voices
- ✅ List all available voices
- ✅ Custom voice entry
- ✅ Link to voice browser
- ✅ Automatic download and installation

### Direct Command
```powershell
python -m piper.download_voices en_US-lessac-medium --data-dir ./models
```

### Voice Browser
Visit https://rhasspy.github.io/piper-samples to:
- Listen to voice samples
- Browse all available voices
- Find the exact voice name to download

## Voice Naming Format

Voices use the format: `{language}-{voice_name}-{quality}`

**Examples:**
- `en_US-lessac-medium`
- `en_US-libritts-high`
- `en_US-ryan-high`

**Quality Levels:**
- `x_low` - 16Khz, 5-7M params
- `low` - 16Khz, 15-20M params  
- `medium` - 22.05Khz, 15-20M params (recommended)
- `high` - 22.05Khz, 28-32M params

## Recommended Voices

1. **en_US-libritts-high** - 903 speakers (male & female) - BEST FOR VARIETY
2. **en_US-lessac-medium** - Female voice (clear, professional)
3. **en_US-ryan-high** - Male voice (clear, professional)
4. **en_US-amy-medium** - Female voice (natural)

## Installation Steps

1. **Install Piper** (if not already installed):
   ```powershell
   pip install piper-tts
   ```

2. **Download a voice**:
   ```powershell
   python setup_models.py
   ```

3. **Start the server**:
   ```powershell
   python -m app.main
   ```

## Why This Change?

**Old Method** (Manual GitHub downloads):
- ❌ Fixed URLs that break when releases change
- ❌ Manual download and extraction
- ❌ Limited to hardcoded voices
- ❌ No way to browse voices

**New Method** (Piper's download API):
- ✅ Always uses latest voice versions
- ✅ Automatic download and setup
- ✅ Access to ALL Piper voices
- ✅ Built-in voice listing
- ✅ Official and maintained

## Troubleshooting

**"ModuleNotFoundError: No module named 'piper'"**
```powershell
pip install piper-tts
```

**"Download failed"**
- Check internet connection
- Try a different voice
- Ensure you have enough disk space

**"Model not found after download"**
- Check the `models/` directory
- Verify the voice name is correct
- Try downloading again

## More Information

- Voice samples: https://rhasspy.github.io/piper-samples
- Piper repository: https://github.com/OHF-Voice/piper1-gpl
- CLI documentation: https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/CLI.md

---

**Last Updated**: January 30, 2026
