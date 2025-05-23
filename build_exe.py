"""
CoresAI Executable Builder
Packages the entire CoresAI system into a standalone executable
"""

import os
import sys
import shutil
import subprocess
import PyInstaller.__main__
from PIL import Image
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def convert_png_to_ico(png_path: str, ico_path: str) -> bool:
    """Convert PNG to ICO format for Windows executable."""
    try:
        if not os.path.exists(png_path):
            logger.error(f"PNG file not found: {png_path}")
            return False
            
        # Open and convert the image
        img = Image.open(png_path)
        img.save(ico_path, format='ICO')
        logger.info(f"Successfully converted {png_path} to {ico_path}")
        return True
    except Exception as e:
        logger.error(f"Error converting PNG to ICO: {str(e)}")
        return False

def create_executable():
    """Create the CoresAI executable."""
    try:
        # Current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Working directory: {current_dir}")
        
        # Convert header image to ico
        png_path = os.path.join(current_dir, "header_image.png")
        ico_path = os.path.join(current_dir, "coresai.ico")
        
        logger.info("Converting header image to icon...")
        if not convert_png_to_ico(png_path, ico_path):
            logger.warning("Failed to convert icon, proceeding without custom icon")
            ico_path = None

        # Create dist directory if it doesn't exist
        dist_dir = os.path.join(current_dir, "dist")
        if not os.path.exists(dist_dir):
            os.makedirs(dist_dir)
            logger.info(f"Created dist directory: {dist_dir}")

        # Create main.py if it doesn't exist
        main_path = os.path.join(current_dir, "gui_app.py")  # Changed to use gui_app.py directly
        if not os.path.exists(main_path):
            logger.error("gui_app.py not found!")
            return

        # Define PyInstaller arguments
        args = [
            main_path,  # Your main script
            '--name=CoresAI',
            '--onefile',  # Create a single executable
            '--noconsole',  # Don't show console window
            '--clean',  # Clean cache
            f'--icon={ico_path}' if ico_path else '',
            '--add-data=src;src',  # Include source files
            '--add-data=frontend/build;frontend/build',  # Include frontend build
            '--add-data=*.json;.',  # Include JSON files
            '--add-data=*.png;.',  # Include images
            '--add-data=*.ico;.',  # Include icons
            '--hidden-import=wmi',
            '--hidden-import=win32com.client',
            '--hidden-import=pythoncom',
            '--hidden-import=discord',
            '--hidden-import=pandas',
            '--hidden-import=numpy',
            '--hidden-import=PIL',
            '--hidden-import=requests',
            '--hidden-import=asyncio',
            '--hidden-import=aiohttp',
            '--hidden-import=PyQt5',
            '--hidden-import=PyQt5.QtCore',
            '--hidden-import=PyQt5.QtGui',
            '--hidden-import=PyQt5.QtWidgets',
            '--hidden-import=psutil',
            '--hidden-import=ccxt',
            '--hidden-import=web3',
            '--hidden-import=eth_account',
            '--hidden-import=cryptography',
            '--hidden-import=redis',
            '--hidden-import=fastapi',
            '--hidden-import=uvicorn',
            '--hidden-import=websockets',
            '--hidden-import=schedule',
            '--hidden-import=hmac',
            '--hidden-import=hashlib',
            '--hidden-import=base64',
            '--hidden-import=json',
            '--hidden-import=time',
            '--hidden-import=datetime',
            '--hidden-import=threading',
            '--hidden-import=queue',
            '--hidden-import=logging',
            '--hidden-import=os',
            '--hidden-import=sys',
            '--distpath=' + dist_dir,  # Specify dist directory
            '--workpath=' + os.path.join(current_dir, "build"),  # Specify build directory
            '--specpath=' + current_dir,  # Specify spec file directory
        ]

        # Filter out empty arguments
        args = [arg for arg in args if arg]

        logger.info("Starting PyInstaller build process...")
        logger.info(f"Build arguments: {' '.join(args)}")

        # Run PyInstaller
        PyInstaller.__main__.run(args)
        
        # Clean up
        if os.path.exists(ico_path):
            os.remove(ico_path)
            logger.info("Cleaned up temporary icon file")
            
        # Verify executable was created
        exe_path = os.path.join(dist_dir, "CoresAI.exe")
        if os.path.exists(exe_path):
            logger.info(f"Successfully created executable: {exe_path}")
            logger.info(f"File size: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
        else:
            logger.error("Failed to create executable!")
        
    except Exception as e:
        logger.error(f"Error creating executable: {str(e)}", exc_info=True)
        raise

def create_main_file():
    """Create the main entry point file."""
    main_content = """import os
import sys
import logging
from src.license_validator import validate_and_activate_key
from src.discord_channels import setup_discord_channels
from src.discord_integration import run_discord_bot
import asyncio
import tkinter as tk
from tkinter import messagebox, ttk
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoresAILauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CoresAI Launcher")
        self.root.geometry("400x300")
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # License key entry
        ttk.Label(main_frame, text="Enter License Key:").grid(row=0, column=0, pady=10)
        self.key_entry = ttk.Entry(main_frame, width=40)
        self.key_entry.grid(row=1, column=0, pady=5)
        
        # Activate button
        ttk.Button(main_frame, text="Activate & Launch", 
                  command=self.activate_and_launch).grid(row=2, column=0, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=300, mode='indeterminate')
        self.progress.grid(row=3, column=0, pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=4, column=0, pady=10)
        
    def activate_and_launch(self):
        key = self.key_entry.get().strip()
        if not key:
            messagebox.showerror("Error", "Please enter a license key")
            return
            
        self.progress.start()
        self.status_label.config(text="Validating license key...")
        
        # Run validation in a separate thread
        threading.Thread(target=self._validate_and_launch, args=(key,), 
                       daemon=True).start()
    
    def _validate_and_launch(self, key):
        try:
            # Validate license key
            success, message = validate_and_activate_key(key)
            
            if not success:
                self.root.after(0, lambda: self._show_error(message))
                return
                
            # Update status
            self.root.after(0, lambda: self.status_label.config(
                text="License validated! Starting CoresAI..."))
            
            # Start the system
            self._start_coresai()
            
        except Exception as e:
            self.root.after(0, lambda: self._show_error(str(e)))
        finally:
            self.root.after(0, self.progress.stop)
    
    def _show_error(self, message):
        self.progress.stop()
        self.status_label.config(text="")
        messagebox.showerror("Error", message)
    
    def _start_coresai(self):
        try:
            # Start Discord bot in a separate thread
            threading.Thread(target=self._run_discord_bot, 
                           daemon=True).start()
            
            # Start other components here
            # ...
            
            # Update UI
            self.root.after(0, lambda: self.status_label.config(
                text="CoresAI is running!"))
            
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Error starting CoresAI: {str(e)}"))
    
    def _run_discord_bot(self):
        try:
            asyncio.run(run_discord_bot())
        except Exception as e:
            logger.error(f"Discord bot error: {str(e)}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CoresAILauncher()
    app.run()
"""
    
    with open('main.py', 'w') as f:
        f.write(main_content)
    logger.info("Created main.py entry point")

if __name__ == "__main__":
    create_executable() 