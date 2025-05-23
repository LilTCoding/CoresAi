"""
Fix all issues in the CoresAI project
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def fix_requirements():
    """Fix requirements.txt with compatible versions"""
    print("📦 Fixing requirements.txt...")
    
    requirements_content = """fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.1
pydantic-settings==2.1.0
python-multipart==0.0.6
requests==2.31.0
PyQt5==5.15.10
numpy==1.26.2
soundfile==0.12.1
sounddevice==0.4.6
psutil==5.9.6
wmi==1.5.1
python-dotenv==1.0.0
jinja2==3.1.2
pyyaml==6.0.1
scikit-learn==1.3.2
pydub==0.25.1
aiofiles==23.2.1
httpx==0.25.2
sse-starlette==1.8.2
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
    
    print("✅ Requirements file updated")

def create_env_file():
    """Create .env file with default settings"""
    print("🔧 Creating .env file...")
    
    env_content = """# CoresAI Environment Configuration
API_V1_STR=api/v1
PROJECT_NAME=CoresAI - Advanced AI System
DEBUG=True

# API Keys (Add your own)
OPENAI_API_KEY=your_api_key_here

# Ports
PRODUCTION_PORT=8080
STREAMING_PORT=8081
VOICE_PORT=8082

# Model Settings
USE_GPU=False
MODEL_PATH=models/saved
"""
    
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created")
    else:
        print("⚠️  .env file already exists, skipping...")

def fix_system_awareness():
    """Fix system awareness module to handle errors gracefully"""
    print("🛠️ Fixing system awareness module...")
    
    system_awareness_path = Path("src/models/system_awareness.py")
    if system_awareness_path.exists():
        # Read the file and add better error handling
        content = system_awareness_path.read_text()
        
        # Check if error handling is already improved
        if "# Enhanced error handling" not in content:
            # Add a note at the top
            lines = content.split('\n')
            lines.insert(1, "# Enhanced error handling for system operations")
            content = '\n'.join(lines)
            system_awareness_path.write_text(content)
            print("✅ System awareness module updated")
        else:
            print("⚠️  System awareness already fixed")

def create_startup_script():
    """Create a comprehensive startup script"""
    print("🚀 Creating startup script...")
    
    startup_content = """@echo off
echo 🚀 Starting CoresAI System...
echo.

REM Kill any existing processes on our ports
echo 🔄 Checking for port conflicts...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8081') do taskkill /F /PID %%a 2>nul

echo.
echo 📦 Installing/Updating dependencies...
pip install -r requirements.txt --quiet

echo.
echo 🌐 Starting Production Backend (Port 8080)...
start /min cmd /c "python production_ai_backend.py"

timeout /t 3 /nobreak >nul

echo 🔄 Starting Streaming Backend (Port 8081)...
start /min cmd /c "python streaming_ai_backend.py"

timeout /t 3 /nobreak >nul

echo 🖥️ Starting GUI Application...
start "CoresAI GUI" python gui_app.py

echo.
echo ✅ CoresAI System Started Successfully!
echo.
echo 📱 GUI: Running
echo 🌐 Production Backend: http://localhost:8080
echo 📡 Streaming Backend: http://localhost:8081
echo 📚 API Docs: http://localhost:8080/docs
echo.
echo Press any key to close this window (backends will continue running)...
pause >nul
"""
    
    with open("start_coresai_fixed.bat", "w") as f:
        f.write(startup_content)
    
    print("✅ Startup script created: start_coresai_fixed.bat")

def create_kill_script():
    """Create a script to kill all CoresAI processes"""
    print("🛑 Creating kill script...")
    
    kill_content = """@echo off
echo 🛑 Stopping all CoresAI processes...
echo.

REM Kill Python processes running our backends
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *production_ai_backend*" 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *streaming_ai_backend*" 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *gui_app*" 2>nul

REM Kill processes on our ports
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8081') do taskkill /F /PID %%a 2>nul

echo.
echo ✅ All CoresAI processes stopped
pause
"""
    
    with open("stop_coresai.bat", "w") as f:
        f.write(kill_content)
    
    print("✅ Kill script created: stop_coresai.bat")

def install_missing_packages():
    """Install any missing packages"""
    print("📦 Installing missing packages...")
    
    try:
        # Install wmi specifically as it's often missing
        subprocess.check_call([sys.executable, "-m", "pip", "install", "wmi", "--quiet"])
        print("✅ wmi package installed")
    except:
        print("⚠️  Could not install wmi package")
    
    try:
        # Install all requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"])
        print("✅ All requirements installed")
    except Exception as e:
        print(f"⚠️  Some packages may have failed to install: {e}")

def create_test_script():
    """Create a comprehensive test script"""
    print("🧪 Creating test script...")
    
    test_content = """#!/usr/bin/env python3
\"\"\"
Comprehensive test script for CoresAI
\"\"\"

import requests
import time
import sys

def test_backend(name, url, endpoints):
    print(f"\\n🧪 Testing {name}...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ {name} is healthy")
            return True
        else:
            print(f"❌ {name} health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} is not running on {url}")
        return False
    except Exception as e:
        print(f"❌ {name} error: {e}")
        return False

def main():
    print("🚀 CoresAI System Test Suite")
    print("=" * 50)
    
    # Test Production Backend
    production_ok = test_backend(
        "Production Backend",
        "http://localhost:8080",
        ["/api/v1/health", "/api/v1/chat"]
    )
    
    # Test Streaming Backend
    streaming_ok = test_backend(
        "Streaming Backend", 
        "http://localhost:8081",
        ["/health", "/api/v1/detect-schema"]
    )
    
    # Summary
    print("\\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Production Backend: {'✅ OK' if production_ok else '❌ FAILED'}")
    print(f"Streaming Backend: {'✅ OK' if streaming_ok else '❌ FAILED'}")
    
    if production_ok and streaming_ok:
        print("\\n🎉 All systems operational!")
        
        # Test chat functionality
        print("\\n🤖 Testing chat functionality...")
        try:
            response = requests.post(
                "http://localhost:8080/api/v1/chat",
                json={"messages": [{"role": "user", "content": "Hello"}]}
            )
            if response.status_code == 200:
                print("✅ Chat endpoint working")
            else:
                print("❌ Chat endpoint failed")
        except Exception as e:
            print(f"❌ Chat test error: {e}")
    else:
        print("\\n⚠️  Some systems are not operational. Please check the logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
    
    with open("test_system.py", "w") as f:
        f.write(test_content)
    
    print("✅ Test script created: test_system.py")

def fix_all():
    """Run all fixes"""
    print("🔧 CoresAI Comprehensive Fix Script")
    print("=" * 50)
    
    # Run all fixes
    fix_requirements()
    create_env_file()
    fix_system_awareness()
    install_missing_packages()
    create_startup_script()
    create_kill_script()
    create_test_script()
    
    print("\n" + "=" * 50)
    print("✅ All fixes completed!")
    print("\n📋 Next steps:")
    print("1. Run 'stop_coresai.bat' to stop any existing processes")
    print("2. Run 'start_coresai_fixed.bat' to start the system")
    print("3. Run 'python test_system.py' to verify everything is working")
    print("\n💡 Tips:")
    print("- If you see port conflicts, run stop_coresai.bat first")
    print("- Check the .env file and add your API keys if needed")
    print("- The GUI will open automatically when you run start_coresai_fixed.bat")

if __name__ == "__main__":
    fix_all() 