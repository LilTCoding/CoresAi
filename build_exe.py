"""
CoresAI Build Script
Packages the entire AI application into a standalone executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")

def create_spec_file():
    """Create PyInstaller spec file for the AI application"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Main GUI application
gui_analysis = Analysis(
    ['gui_app.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('dragon_logo.png', '.'),
        ('header_image.png', '.'),
        ('data', 'data'),
        ('models', 'models'),
        ('src', 'src'),
        ('production_ai_backend.py', '.'),
        ('test_ai_interface.html', '.'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'requests',
        'pydantic',
        'numpy',
        'psutil',
        'wmi',
        'sounddevice',
        'soundfile',
        'multiprocessing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'bark',
        'torch',
        'transformers',
        'tensorflow',
        'matplotlib',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

gui_pyz = PYZ(gui_analysis.pure, gui_analysis.zipped_data, cipher=block_cipher)

gui_exe = EXE(
    gui_pyz,
    gui_analysis.scripts,
    [],
    exclude_binaries=True,
    name='CoresAI-GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='dragon_logo.png' if os.path.exists('dragon_logo.png') else None,
)

# Backend application
backend_analysis = Analysis(
    ['production_ai_backend.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('data', 'data'),
        ('models', 'models'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'pydantic',
        'requests',
        'numpy',
        'psutil',
        'wmi',
        'multiprocessing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'bark',
        'torch', 
        'transformers',
        'tensorflow',
        'matplotlib',
        'pandas',
        'PyQt5',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

backend_pyz = PYZ(backend_analysis.pure, backend_analysis.zipped_data, cipher=block_cipher)

backend_exe = EXE(
    backend_pyz,
    backend_analysis.scripts,
    [],
    exclude_binaries=True,
    name='CoresAI-Backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Collect everything into a distribution folder
coll = COLLECT(
    gui_exe,
    gui_analysis.binaries,
    gui_analysis.zipfiles,
    gui_analysis.datas,
    backend_exe,
    backend_analysis.binaries,
    backend_analysis.zipfiles,
    backend_analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CoresAI-Distribution',
)
'''
    
    with open('CoresAI.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created PyInstaller spec file: CoresAI.spec")

def create_launcher_script():
    """Create a launcher script to start both backend and GUI"""
    launcher_content = '''@echo off
title CoresAI - Advanced AI Assistant
echo.
echo 🚀 Starting CoresAI Advanced AI Assistant...
echo.
echo ⚡ Initializing backend server...
start /min "CoresAI Backend" CoresAI-Backend.exe

echo 🔄 Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo 🖥️  Starting GUI application...
start "CoresAI GUI" CoresAI-GUI.exe

echo.
echo ✅ CoresAI is now running!
echo 📱 GUI: CoresAI main interface
echo 🌐 Backend: http://localhost:8080
echo 📚 API Docs: http://localhost:8080/docs
echo.
echo Press any key to close this window...
pause >nul
'''
    
    with open('Start-CoresAI.bat', 'w') as f:
        f.write(launcher_content)
    
    print("✅ Created launcher script: Start-CoresAI.bat")

def create_readme():
    """Create a distribution README"""
    readme_content = '''# CoresAI - Advanced AI Assistant

## 🚀 Quick Start

1. Double-click `Start-CoresAI.bat` to launch the complete AI system
2. The GUI will open automatically with the backend running in the background
3. Start chatting with your AI assistant!

## 📁 Files Included

- `CoresAI-GUI.exe` - Main graphical interface
- `CoresAI-Backend.exe` - AI backend server  
- `Start-CoresAI.bat` - Easy launcher script
- `test_ai_interface.html` - Web interface (optional)
- `README.md` - This file

## ✨ Features

🔍 **Web Search & Real-time Data** - Current information from the web
🧠 **Advanced Reasoning** - Complex problem-solving and analysis  
💬 **Natural Conversations** - Context-aware dialogue
📊 **Data Analysis** - Processing and interpreting information
🎯 **Personalized Assistance** - Adaptive to your specific needs

## 🌐 Web Interface

You can also use the web interface by:
1. Starting the backend: `CoresAI-Backend.exe`
2. Opening `test_ai_interface.html` in your browser

## 🔧 Manual Operation

If you prefer to run components separately:

**Backend Only:**
```
CoresAI-Backend.exe
```

**GUI Only:**
```
CoresAI-GUI.exe
```

## 📱 System Requirements

- Windows 10/11
- 4GB RAM minimum (8GB recommended)
- Internet connection for web search features

## 🆘 Troubleshooting

**GUI doesn't appear:**
- Make sure the backend is running first
- Check Windows Defender/antivirus settings
- Run as administrator if needed

**Backend connection issues:**
- Check if port 8080 is available
- Restart both applications
- Check firewall settings

## 📞 Support

For support and updates, please refer to the original project documentation.

---
**CoresAI v3.0.0 - Production Ready**
'''
    
    with open('DISTRIBUTION-README.md', 'w') as f:
        f.write(readme_content)
    
    print("✅ Created distribution README: DISTRIBUTION-README.md")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building CoresAI executable...")
    print("⏳ This may take several minutes...")
    
    try:
        # Run PyInstaller with the spec file
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller", 
            "--clean", "--noconfirm", "CoresAI.spec"
        ])
        print("✅ Build completed successfully!")
        
        # Create additional files in the dist folder
        dist_path = Path("dist/CoresAI-Distribution")
        if dist_path.exists():
            # Copy launcher script
            shutil.copy("Start-CoresAI.bat", dist_path)
            shutil.copy("DISTRIBUTION-README.md", dist_path / "README.md")
            shutil.copy("test_ai_interface.html", dist_path)
            
            print(f"📦 Distribution ready in: {dist_path}")
            print("🎉 Your AI application is ready to distribute!")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

def main():
    """Main build process"""
    print("🚀 CoresAI Build Process Starting...")
    print("=" * 50)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create necessary files
    create_spec_file()
    create_launcher_script() 
    create_readme()
    
    # Build the executable
    if build_executable():
        print("\n🎉 BUILD SUCCESSFUL!")
        print("=" * 50)
        print("📦 Your CoresAI application is ready for distribution!")
        print("📁 Find it in: dist/CoresAI-Distribution/")
        print("🚀 Run: Start-CoresAI.bat to test")
    else:
        print("\n❌ BUILD FAILED!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main() 