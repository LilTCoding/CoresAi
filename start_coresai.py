import os
import sys
import time
import subprocess
import signal
import psutil
import webbrowser
from pathlib import Path
from network_utils import setup_network, kill_process_on_port

class CoresAILauncher:
    def __init__(self):
        self.processes = []
        self.root_dir = Path(__file__).parent.absolute()
        self.frontend_dir = self.root_dir / 'frontend'
        self.local_ip = None
        self.backend_port = None
        self.frontend_port = None
        
    def setup_environment(self):
        """Configure network and environment."""
        print("Setting up network configuration...")
        self.local_ip, self.backend_port, self.frontend_port = setup_network()
        
        # Update environment variables for child processes
        os.environ['CORESAI_IP'] = self.local_ip
        os.environ['CORESAI_BACKEND_PORT'] = str(self.backend_port)
        os.environ['CORESAI_FRONTEND_PORT'] = str(self.frontend_port)
        
        # Create .env file for frontend
        env_content = f"""
REACT_APP_BACKEND_URL=http://{self.local_ip}:{self.backend_port}
REACT_APP_WS_URL=ws://{self.local_ip}:{self.backend_port}
PORT={self.frontend_port}
"""
        with open(self.frontend_dir / '.env', 'w') as f:
            f.write(env_content.strip())

    def start_backend(self):
        print("Starting CoresAI Backend...")
        backend_process = subprocess.Popen(
            [sys.executable, 'production_ai_backend.py'],
            cwd=self.root_dir,
            env=dict(os.environ),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        self.processes.append(backend_process)
        time.sleep(2)  # Wait for backend to start

    def start_frontend(self):
        print("Starting CoresAI Frontend...")
        # Install frontend dependencies if node_modules doesn't exist
        if not (self.frontend_dir / 'node_modules').exists():
            print("Installing frontend dependencies...")
            subprocess.run(['npm', 'install', '--legacy-peer-deps'], cwd=self.frontend_dir, check=True)

        # Run npm start in a new console
        frontend_process = subprocess.Popen(
            'cmd /c "cd frontend && npm start"',
            shell=True,
            env=dict(os.environ),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        self.processes.append(frontend_process)
        time.sleep(2)  # Wait for frontend to start

    def start_gui(self):
        print("Starting CoresAI GUI...")
        gui_process = subprocess.Popen(
            [sys.executable, 'gui_app.py'],
            cwd=self.root_dir,
            env=dict(os.environ),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        self.processes.append(gui_process)

    def open_browser(self):
        time.sleep(3)  # Wait for services to be ready
        webbrowser.open(f'http://{self.local_ip}:{self.frontend_port}')  # Frontend
        webbrowser.open(f'http://{self.local_ip}:{self.backend_port}/docs')  # Backend docs

    def cleanup(self, *args):
        print("\nShutting down CoresAI...")
        for process in self.processes:
            try:
                process.kill()
            except:
                pass
        
        # Kill any remaining processes on our ports
        if self.backend_port:
            kill_process_on_port(self.backend_port)
        if self.frontend_port:
            kill_process_on_port(self.frontend_port)
            
        sys.exit(0)

    def start(self):
        try:
            # Register cleanup handler
            signal.signal(signal.SIGINT, self.cleanup)
            signal.signal(signal.SIGTERM, self.cleanup)

            print("=== Starting CoresAI System ===")
            self.setup_environment()
            self.start_backend()
            self.start_frontend()
            self.start_gui()
            self.open_browser()
            
            print("\nCoresAI is running!")
            print(f"Frontend: http://{self.local_ip}:{self.frontend_port}")
            print(f"Backend API: http://{self.local_ip}:{self.backend_port}")
            print(f"Backend Docs: http://{self.local_ip}:{self.backend_port}/docs")
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