import os
import sys
import time
import subprocess
import signal
import psutil
import webbrowser
from pathlib import Path

class CoresAILauncher:
    def __init__(self):
        self.processes = []
        self.root_dir = Path(__file__).parent.absolute()
        self.frontend_dir = self.root_dir / 'frontend'
        
    def kill_process_on_port(self, port):
        for proc in psutil.process_iter(['pid']):
            try:
                connections = proc.connections()
                for conn in connections:
                    if hasattr(conn, 'laddr') and conn.laddr.port == port:
                        proc.kill()
                        time.sleep(1)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error):
                continue

    def start_backend(self):
        print("Starting CoresAI Backend...")
        # Kill any process using port 8080
        self.kill_process_on_port(8080)
        
        backend_process = subprocess.Popen(
            [sys.executable, 'production_ai_backend.py'],
            cwd=self.root_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        self.processes.append(backend_process)
        time.sleep(2)  # Wait for backend to start

    def start_frontend(self):
        print("Starting CoresAI Frontend...")
        # Install frontend dependencies if node_modules doesn't exist
        if not (self.frontend_dir / 'node_modules').exists():
            print("Installing frontend dependencies...")
            subprocess.run(['npm', 'install'], cwd=self.frontend_dir, check=True)

        # Run npm start in a new console
        frontend_process = subprocess.Popen(
            'cmd /c "cd frontend && npm start"',
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        self.processes.append(frontend_process)
        time.sleep(2)  # Wait for frontend to start

    def start_gui(self):
        print("Starting CoresAI GUI...")
        gui_process = subprocess.Popen(
            [sys.executable, 'gui_app.py'],
            cwd=self.root_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        self.processes.append(gui_process)

    def open_browser(self):
        time.sleep(3)  # Wait for services to be ready
        webbrowser.open('http://localhost:3000')  # Frontend
        webbrowser.open('http://localhost:8080/docs')  # Backend docs

    def cleanup(self, *args):
        print("\nShutting down CoresAI...")
        for process in self.processes:
            try:
                process.kill()
            except:
                pass
        sys.exit(0)

    def start(self):
        try:
            # Register cleanup handler
            signal.signal(signal.SIGINT, self.cleanup)
            signal.signal(signal.SIGTERM, self.cleanup)

            print("=== Starting CoresAI System ===")
            self.start_backend()
            self.start_frontend()
            self.start_gui()
            self.open_browser()
            
            print("\nCoresAI is running!")
            print("Frontend: http://localhost:3000")
            print("Backend API: http://localhost:8080")
            print("Backend Docs: http://localhost:8080/docs")
            print("\nPress Ctrl+C to stop all services.")
            
            # Keep the script running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            print(f"Error: {e}")
            self.cleanup()

if __name__ == "__main__":
    launcher = CoresAILauncher()
    launcher.start() 