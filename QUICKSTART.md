# Quick Start Guide

## Installation (5 minutes)

### 1. Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Download Voice Models
```powershell
python setup_models.py
```
Choose option **1** (en_US-libritts-high) for the best multi-speaker model.

**Or browse voices online:**
Visit https://rhasspy.github.io/piper-samples to see all available voices and hear samples.

### 3. Start the Server
```powershell
python -m app.main
```

### 4. Test It!

**Option A: Web Browser**
- Open: http://localhost:8000
- Enter text and click "Generate Speech"

**Option B: Python Client**
```powershell
python test_client.py "Hello from the offline TTS system"
```

## Accessing from Other Computers

1. **Find your IP address:**
   ```powershell
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. **On other computers:**
   - Open: http://192.168.1.100:8000

3. **Allow firewall access:**
   ```powershell
   New-NetFirewallRule -DisplayName "TTS Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

## Voice Selection

The libritts-high model has 903 speakers. Try different `speaker_id` values:
- **0-450**: Mostly female voices
- **450-903**: Mostly male voices

Example:
```python
{
  "text": "Hello",
  "speaker_id": 0,    # Female
  "speed": 1.0
}
```

## Troubleshooting

**"Piper executable not found"**
```powershell
pip install piper-tts
```

**"Model file not found"**
```powershell
python setup_models.py
```

**Server won't start on port 8000**
- Edit `.env` file and change PORT to 8001

## Need Help?

Check the full README.md for detailed documentation.
