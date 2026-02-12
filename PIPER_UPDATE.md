# Important Update - Piper Repository Change

## Repository Migration

**Piper TTS has moved to a new repository:**

- **Old Repository**: https://github.com/rhasspy/piper (archived/deprecated)
- **New Repository**: https://github.com/OHF-Voice/piper1-gpl (active)

## What Changed?

All documentation and scripts in this project have been updated to reference the new repository:

### Updated Files:
- ✅ `README.md` - Installation instructions and download links
- ✅ `setup_models.py` - Model download URLs
- ✅ `QUICKSTART.md` - Quick start guide
- ✅ `PROJECT_SUMMARY.md` - Project overview

### What You Need to Do:

**If you haven't installed yet:**
- Just follow the normal installation process - everything is already updated

**If you already installed from old URLs:**
- The old models still work fine! No need to re-download
- If you need new models, use: `python setup_models.py` (now uses new URLs)

## Installation (Updated)

### Install Piper:
```powershell
pip install piper-tts
```

### Download Models:
```powershell
python setup_models.py
```

The script now downloads from: `https://github.com/OHF-Voice/piper1-gpl/releases`

## Model Compatibility

All existing Piper models (.onnx files) are fully compatible. No changes needed to:
- Your existing code
- Model files you already downloaded
- The TTS engine implementation

## More Information

Visit the new repository for:
- Latest releases: https://github.com/OHF-Voice/piper1-gpl/releases
- Documentation: https://github.com/OHF-Voice/piper1-gpl
- Bug reports and issues

---

**Last Updated**: January 30, 2026
