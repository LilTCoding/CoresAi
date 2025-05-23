#!/usr/bin/env python3
"""
Fix npm and dependency issues for CoresAI
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n=== {description} ===")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def main():
    print("🔧 Fixing CoresAI npm and dependency issues...")
    
    # Step 1: Fix NumPy compatibility
    print("\n1. Fixing NumPy compatibility...")
    run_command("pip uninstall numpy -y", "Removing incompatible NumPy")
    run_command("pip install numpy==1.26.4", "Installing compatible NumPy")
    
    # Step 2: Reinstall OpenCV
    print("\n2. Reinstalling OpenCV...")
    run_command("pip uninstall opencv-python -y", "Removing OpenCV")
    run_command("pip install opencv-python==4.8.0.74", "Installing compatible OpenCV")
    
    # Step 3: Install concurrently for npm
    print("\n3. Installing Node.js dependencies...")
    run_command("npm install concurrently --save-dev", "Installing concurrently")
    
    # Step 4: Fix Windows encoding
    print("\n4. Setting up Windows encoding...")
    if sys.platform == "win32":
        os.system("chcp 65001 > nul")
        print("✅ Set UTF-8 encoding for Windows")
    
    # Step 5: Create start script without emoji
    print("\n5. Creating start script...")
    start_script = """@echo off
echo === Starting CoresAI System ===
echo Production Backend: http://localhost:8080
echo Streaming Backend: http://localhost:8081
echo.
start cmd /k "python production_ai_backend.py"
timeout /t 3 > nul
start cmd /k "python streaming_ai_backend.py"
echo.
echo === Both backends starting... ===
echo Check the new command windows for status
pause
"""
    
    with open("start_coresai_safe.bat", "w", encoding="utf-8") as f:
        f.write(start_script)
    
    print("✅ Created start_coresai_safe.bat")
    
    print("\n" + "="*50)
    print("🎉 Fixes completed!")
    print("\nTo start your system:")
    print("1. Run: start_coresai_safe.bat")
    print("2. Or run: npm run start")
    print("3. Or manually: python production_ai_backend.py (then streaming_ai_backend.py)")
    print("\nGUI: python gui_app.py")

if __name__ == "__main__":
    main() 