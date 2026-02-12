"""
System verification script - checks if everything is properly installed
"""
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("[*] Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"  [OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  [FAIL] Python {version.major}.{version.minor}.{version.micro} (Need 3.9+)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\n[*] Checking dependencies...")
    
    required = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'websockets': 'WebSockets',
        'pydantic': 'Pydantic',
        'numpy': 'NumPy',
    }
    
    all_ok = True
    for package, name in required.items():
        try:
            __import__(package)
            print(f"  [OK] {name}")
        except ImportError:
            print(f"  [FAIL] {name} (not installed)")
            all_ok = False
    
    return all_ok


def check_piper():
    """Check if Piper is installed"""
    print("\n[*] Checking Piper TTS...")
    
    # Try importing piper_tts
    try:
        import piper
        print(f"  [OK] Piper TTS (Python package)")
        return True
    except ImportError:
        pass
    
    # Try running piper command
    try:
        result = subprocess.run(
            ['piper', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"  [OK] Piper TTS (Executable)")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print(f"  [WARN] Piper TTS (not found - install with: pip install piper-tts)")
    return False


def check_models():
    """Check if models are downloaded"""
    print("\n[*] Checking voice models...")
    
    models_dir = Path(__file__).parent / "models"
    
    if not models_dir.exists():
        print(f"  [FAIL] Models directory not found")
        return False
    
    onnx_files = list(models_dir.glob("*.onnx"))
    
    if onnx_files:
        print(f"  [OK] Found {len(onnx_files)} model(s):")
        for model in onnx_files:
            size_mb = model.stat().st_size / (1024 * 1024)
            print(f"       - {model.name} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  [WARN] No models found (run: python setup_models.py)")
        return False


def check_project_structure():
    """Check if all required files exist"""
    print("\n[*] Checking project structure...")
    
    required_files = [
        "app/main.py",
        "app/config.py",
        "app/api/routes.py",
        "app/api/schemas.py",
        "app/core/tts_engine.py",
        "app/core/viseme_map.py",
        "app/static/index.html",
        "requirements.txt",
    ]
    
    base_dir = Path(__file__).parent
    all_ok = True
    
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"  [OK] {file_path}")
        else:
            print(f"  [FAIL] {file_path}")
            all_ok = False
    
    return all_ok


def check_network():
    """Check network configuration"""
    print("\n[*] Checking network...")
    
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"  [OK] Hostname: {hostname}")
        print(f"  [OK] Local IP: {local_ip}")
        print(f"  [INFO] Server will be accessible at: http://{local_ip}:8000")
        return True
    except Exception as e:
        print(f"  [WARN] Could not determine network info: {e}")
        return True  # Not critical


def main():
    print("=" * 80)
    print("TTS Streaming Server - System Verification")
    print("=" * 80)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Piper TTS", check_piper),
        ("Voice Models", check_models),
        ("Project Structure", check_project_structure),
        ("Network", check_network),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  [ERROR] Error during {name} check: {e}")
            results.append((name, False))
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for name, result in results:
        status = "[PASS]" if result else "[WARN]"
        print(f"  {status:8} {name}")
    
    print()
    
    # Overall status
    all_passed = all(result for _, result in results)
    critical_passed = results[0][1] and results[1][1] and results[4][1]  # Python, deps, structure
    
    # If Qwen3 is default, models are optional
    if settings.TTS_ENGINE == "qwen3":
        pass
    else:
        critical_passed = critical_passed and results[3][1]  # Models required for Piper
    
    if all_passed:
        print("SUCCESS: All checks passed! You're ready to go!")
        print()
        print("Next steps:")
        print("  1. Start server: python -m app.main")
        print("  2. Open browser: http://localhost:8000")
    elif critical_passed:
        print("WARNING: System is functional but some optional features may not work.")
        print()
        print("To fix warnings:")
        if not results[2][1]:  # Piper
            print("  - Install Piper: pip install piper-tts")
        if not results[3][1]:  # Models
            print("  - Download models: python setup_models.py")
    else:
        print("ERROR: Critical issues detected. Please fix the errors above.")
        print()
        print("Common fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Download models: python setup_models.py")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
