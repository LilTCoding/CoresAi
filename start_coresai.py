#!/usr/bin/env python3
"""
CoresAI Startup Script
Handles startup sequence, error handling, and component management
"""

import os
import sys
import json
import time
import signal
import logging
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/coresai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CoresAILauncher:
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.config = self.load_config()
        self.setup_directories()
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

    def load_config(self) -> dict:
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            'logs',
            'data',
            'models',
            'src',
            'experiment_logs'
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def setup_environment(self):
        """Setup virtual environment and install dependencies"""
        try:
            # Create virtual environment if it doesn't exist
            if not Path('venv').exists():
                logger.info("Creating virtual environment...")
                subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)

            # Activate virtual environment
            if sys.platform == 'win32':
                python_path = str(Path('venv/Scripts/python.exe').resolve())
                pip_path = str(Path('venv/Scripts/pip.exe').resolve())
            else:
                python_path = str(Path('venv/bin/python').resolve())
                pip_path = str(Path('venv/bin/pip').resolve())

            # Install requirements
            logger.info("Installing Python dependencies...")
            subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
            subprocess.run([pip_path, 'install', '-r', 'crypto_requirements.txt'], check=True)

            # Install frontend dependencies
            if Path('frontend/package.json').exists():
                logger.info("Installing frontend dependencies...")
                subprocess.run(['npm', 'install', '--prefix', 'frontend'], check=True)

            return python_path
        except Exception as e:
            logger.error(f"Failed to setup environment: {e}")
            return sys.executable

    def start_backend(self, python_path: str):
        """Start all backend services"""
        try:
            # Start production backend
            if self.config['backends']['production']['enabled']:
                port = self.config['backends']['production']['port']
                cmd = [
                    python_path, '-m', 'uvicorn',
                    'production_ai_backend:app',
                    '--host', '0.0.0.0',
                    '--port', str(port),
                    '--reload' if self.config['development']['hot_reload'] else ''
                ]
                self.processes['production'] = subprocess.Popen(cmd)
                logger.info(f"Started production backend on port {port}")

            # Start streaming backend
            if self.config['backends']['streaming']['enabled']:
                port = self.config['backends']['streaming']['port']
                cmd = [
                    python_path, '-m', 'uvicorn',
                    'streaming_ai_backend:app',
                    '--host', '0.0.0.0',
                    '--port', str(port),
                    '--reload' if self.config['development']['hot_reload'] else ''
                ]
                self.processes['streaming'] = subprocess.Popen(cmd)
                logger.info(f"Started streaming backend on port {port}")

        except Exception as e:
            logger.error(f"Failed to start backend services: {e}")
            self.cleanup()

    def start_frontend(self):
        """Start frontend development server"""
        try:
            if Path('frontend/package.json').exists():
                cmd = ['npm', 'start', '--prefix', 'frontend']
                self.processes['frontend'] = subprocess.Popen(cmd)
                logger.info("Started frontend development server")
        except Exception as e:
            logger.error(f"Failed to start frontend: {e}")

    def start_gui(self):
        """Start GUI application if enabled"""
        try:
            if self.config['gui']['enabled']:
                python_path = str(Path('venv/Scripts/python.exe' if sys.platform == 'win32' else 'venv/bin/python').resolve())
                cmd = [python_path, 'gui_app.py']
                self.processes['gui'] = subprocess.Popen(cmd)
                logger.info("Started GUI application")
        except Exception as e:
            logger.error(f"Failed to start GUI: {e}")

    def open_browser(self):
        """Open web interfaces in browser"""
        try:
            time.sleep(3)  # Wait for servers to start
            if self.config['backends']['production']['enabled']:
                webbrowser.open(f"http://localhost:{self.config['backends']['production']['port']}/docs")
            if Path('test_ai_interface.html').exists():
                webbrowser.open('test_ai_interface.html')
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")

    def cleanup(self, *args):
        """Cleanup processes on shutdown"""
        logger.info("Shutting down CoresAI...")
        for name, process in self.processes.items():
            try:
                logger.info(f"Stopping {name}...")
                if sys.platform == 'win32':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)])
                else:
                    process.terminate()
                    process.wait(timeout=5)
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
        sys.exit(0)

    def verify_ports(self) -> bool:
        """Verify required ports are available"""
        import socket
        ports = [
            self.config['backends']['production']['port'],
            self.config['backends']['streaming']['port'],
            3000  # Frontend development server
        ]
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('localhost', port))
                sock.close()
            except socket.error:
                logger.error(f"Port {port} is already in use")
                return False
        return True

    def start(self):
        """Start all CoresAI components"""
        try:
            logger.info("Starting CoresAI...")
            
            # Verify ports are available
            if not self.verify_ports():
                logger.error("Required ports are not available. Please close conflicting applications.")
                return

            # Setup environment
            python_path = self.setup_environment()
            if not python_path:
                return

            # Start components
            self.start_backend(python_path)
            time.sleep(2)  # Wait for backends to start
            
            self.start_frontend()
            time.sleep(1)
            
            if self.config['gui']['enabled']:
                self.start_gui()
            
            self.open_browser()
            
            logger.info("CoresAI started successfully!")
            logger.info("Press Ctrl+C to stop all services")
            
            # Keep the script running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            logger.error(f"Failed to start CoresAI: {e}")
            self.cleanup()

if __name__ == "__main__":
    launcher = CoresAILauncher()
    launcher.start() 