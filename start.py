import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

def kill_process_on_port(port):
    """Kill any process using the specified port"""
    import psutil
    for proc in psutil.process_iter(['pid']):
        try:
            for conn in proc.connections():
                if hasattr(conn, 'laddr') and conn.laddr.port == port:
                    proc.kill()
                    time.sleep(1)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error):
            continue

def start_backend():
    """Start the FastAPI backend"""
    print("\n=== Starting Backend ===")
    kill_process_on_port(8082)
    return subprocess.Popen(
        [sys.executable, 'production_ai_backend.py'],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

def start_frontend():
    """Start the React frontend"""
    print("\n=== Starting Frontend ===")
    os.chdir('frontend')
    npm_path = r"C:\Program Files\nodejs\npm.cmd"
    return subprocess.Popen(
        [npm_path, 'start'],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

def start_gui():
    """Start the PyQt5 GUI"""
    print("\n=== Starting GUI ===")
    return subprocess.Popen(
        [sys.executable, 'gui_app.py'],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

def main():
    try:
        # Ensure we're in the project root
        os.chdir(Path(__file__).parent)
        
        # Start backend
        backend_process = start_backend()
        time.sleep(2)  # Wait for backend to start
        
        # Start frontend
        frontend_process = start_frontend()
        time.sleep(2)  # Wait for frontend to start
        
        # Start GUI
        gui_process = start_gui()
        
        # Open web interfaces
        webbrowser.open('http://localhost:8082/docs')  # Backend docs
        webbrowser.open('http://localhost:3000')      # Frontend
        
        print("\n=== CoresAI System Started ===")
        print("Backend API: http://localhost:8082")
        print("Frontend: http://localhost:3000")
        print("Press Ctrl+C to stop all services")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main() 