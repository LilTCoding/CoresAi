import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys
import os
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
import queue
import psutil
import wmi
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox, QSplashScreen,
    QTabWidget, QListWidget, QFileDialog, QSplitter, QInputDialog, QDialog, QComboBox, 
    QTextBrowser, QProgressBar, QFrame, QScrollArea, QGridLayout, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QPoint, QSize

# Configuration
API_URL = "http://localhost:8082/api/v1"  # Updated to use port 8082
HEADER_IMAGE_PATH = "header_image.png"
SPLASH_IMAGE_PATH = "dragon_logo.png"
SPLASH_DURATION = 2500  # milliseconds

# Server types
SERVER_GAMES = [
    ("FiveM QB", "fivem_qb"),
    ("Minecraft", "minecraft"),
    ("Arma Reforger", "arma_reforger"),
    ("Rust", "rust")
]

# Crypto trading constants
SUPPORTED_COINS = [
    "ETC", "RVN", "XMR", "BTC", "LTC"
]

MINING_POOLS = [
    "Ethermine", "2Miners", "F2Pool", "NiceHash"
]

class HardwareMonitor(QThread):
    hardware_update = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.wmi = wmi.WMI()
        
    def run(self):
        while self.running:
            try:
                # Get GPU info
                gpus = []
                for gpu in self.wmi.Win32_VideoController():
                    gpus.append({
                        'name': gpu.Name,
                        'memory': round(int(gpu.AdapterRAM or 0) / (1024**3), 1),
                        'driver_version': gpu.DriverVersion,
                        'core_clock_mhz': 0,  # Would need vendor-specific APIs
                        'memory_clock_mhz': 0  # Would need vendor-specific APIs
                    })
                
                # Get CPU info
                cpu = next(iter(self.wmi.Win32_Processor()), None)
                cpu_info = {}
                if cpu:
                    cpu_info = {
                        'name': cpu.Name,
                        'cores': cpu.NumberOfCores,
                        'threads': cpu.NumberOfLogicalProcessors,
                        'base_clock': round(cpu.MaxClockSpeed / 1000, 1)
                    }
                
                # Get memory info
                memory = psutil.virtual_memory()
                total_memory = round(memory.total / (1024**3), 1)
                
                # Estimate power supply based on components
                estimated_psu = 750  # Default estimate
                if gpus:
                    estimated_psu = max(850, 750 + len(gpus) * 250)
                
                hardware_info = {
                    'gpus': gpus,
                    'cpu': cpu_info,
                    'total_memory': total_memory,
                    'power_supply': estimated_psu
                }
                
                self.hardware_update.emit(hardware_info)
                
            except Exception as e:
                print(f"Error monitoring hardware: {str(e)}")
                
            time.sleep(5)  # Update every 5 seconds
            
    def stop(self):
        self.running = False
        self.wait()

class MiningWorker(QThread):
    status_update = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, wallet_address: str, coin: str, pool: str):
        super().__init__()
        self.wallet_address = wallet_address
        self.coin = coin
        self.pool = pool
        self.running = True
        self.start_time = time.time()
        
    def run(self):
        while self.running:
            try:
                # Simulate mining metrics (in production, get real data from mining software)
                uptime = time.time() - self.start_time
                hours, remainder = divmod(int(uptime), 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                # Generate simulated mining status
                hashrate = 50 + (time.time() % 10)  # 50-60 MH/s
                power = 150 + (time.time() % 20)  # 150-170W
                temp = 65 + (time.time() % 10)  # 65-75°C
                accepted = int(uptime / 10)  # 1 share per 10 seconds
                rejected = max(0, int(accepted * 0.02))  # 2% reject rate
                
                # Calculate efficiency based on temperature and power
                max_hashrate = 60  # MH/s
                max_power = 170  # W
                temp_penalty = max(0, (temp - 65) / 10)  # Penalty above 65°C
                power_efficiency = 1 - (power - 150) / (max_power - 150)  # Higher power = lower efficiency
                efficiency = max(0, min(100, (hashrate / max_hashrate * 100 - temp_penalty) * power_efficiency))
                
                status = {
                    'is_running': True,
                    'hashrate': hashrate,
                    'power_consumption': power,
                    'temperature': temp,
                    'accepted_shares': accepted,
                    'rejected_shares': rejected,
                    'uptime': uptime_str,
                    'efficiency': efficiency
                }
                
                self.status_update.emit(status)
                
            except Exception as e:
                self.error.emit(str(e))
                
            time.sleep(1)  # Update every second
            
    def stop(self):
        self.running = False
        self.wait()

class BoostSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(100, 100)
        self.value = 0  # 0 to 100
        self.target_value = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate)
        self.animation_timer.start(16)  # ~60 FPS
        
    def set_value(self, value):
        self.target_value = max(0, min(100, value))
        
    def animate(self):
        if self.value != self.target_value:
            diff = self.target_value - self.value
            self.value += diff * 0.1  # Smooth animation
            self.update()
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        size = min(width, height)
        x = (width - size) // 2
        y = (height - size) // 2
        
        # Draw background circle
        painter.setPen(QPen(QColor("#3f3f3f"), 8))
        painter.drawEllipse(x + 4, y + 4, size - 8, size - 8)
        
        # Draw progress arc
        if self.value > 0:
            painter.setPen(QPen(QColor("#00ff00"), 8))
            span = int(-self.value * 360 / 100 * 16)  # QPainter uses 16th of a degree
            painter.drawArc(x + 4, y + 4, size - 8, size - 8, 90 * 16, span)
        
        # Draw text
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Arial", size // 8, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, f"{int(self.value)}%")

class CryptoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.wallet_address = ""
        self.mining_status = {}
        self.mining_earnings = {}
        self.hardware_info = {}
        self.mining_worker = None
        self.hardware_monitor = HardwareMonitor()
        self.hardware_monitor.hardware_update.connect(self.update_hardware_info)
        self._init_ui()
        self.hardware_monitor.start()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Top section with wallet and boost spinner
        top_layout = QHBoxLayout()
        
        # Wallet Connection (left side)
        wallet_group = QFrame()
        wallet_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        wallet_layout = QVBoxLayout()
        wallet_group.setLayout(wallet_layout)

        wallet_header = QLabel("Wallet Connection")
        wallet_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        wallet_layout.addWidget(wallet_header)

        wallet_input = QHBoxLayout()
        self.wallet_address_input = QLineEdit()
        self.wallet_address_input.setPlaceholderText("Enter wallet address...")
        self.connect_wallet_btn = QPushButton("Connect Wallet")
        self.connect_wallet_btn.clicked.connect(self.connect_wallet)
        wallet_input.addWidget(self.wallet_address_input)
        wallet_input.addWidget(self.connect_wallet_btn)
        wallet_layout.addLayout(wallet_input)
        
        top_layout.addWidget(wallet_group, stretch=2)
        
        # Boost Spinner (right side)
        spinner_group = QFrame()
        spinner_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        spinner_layout = QVBoxLayout()
        spinner_group.setLayout(spinner_layout)
        
        spinner_header = QLabel("Mining Power")
        spinner_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        spinner_header.setAlignment(Qt.AlignCenter)
        spinner_layout.addWidget(spinner_header)
        
        self.boost_spinner = BoostSpinner()
        spinner_layout.addWidget(self.boost_spinner)
        
        top_layout.addWidget(spinner_group, stretch=1)
        
        layout.addLayout(top_layout)

        # Mining Controls
        mining_group = QFrame()
        mining_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        mining_layout = QVBoxLayout()
        mining_group.setLayout(mining_layout)

        mining_header = QLabel("Mining Controls")
        mining_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        mining_layout.addWidget(mining_header)

        # Coin Selection
        coin_layout = QHBoxLayout()
        coin_layout.addWidget(QLabel("Coin:"))
        self.coin_combo = QComboBox()
        self.coin_combo.addItems(SUPPORTED_COINS)
        coin_layout.addWidget(self.coin_combo)
        mining_layout.addLayout(coin_layout)

        # Pool Selection
        pool_layout = QHBoxLayout()
        pool_layout.addWidget(QLabel("Pool:"))
        self.pool_combo = QComboBox()
        self.pool_combo.addItems(MINING_POOLS)
        pool_layout.addWidget(self.pool_combo)
        mining_layout.addLayout(pool_layout)

        # Mining Control Buttons
        control_layout = QHBoxLayout()
        self.start_mining_btn = QPushButton("Start Mining")
        self.start_mining_btn.clicked.connect(self.start_mining)
        self.stop_mining_btn = QPushButton("Stop Mining")
        self.stop_mining_btn.clicked.connect(self.stop_mining)
        self.stop_mining_btn.setEnabled(False)
        control_layout.addWidget(self.start_mining_btn)
        control_layout.addWidget(self.stop_mining_btn)
        mining_layout.addLayout(control_layout)

        layout.addWidget(mining_group)

        # Mining Status
        status_group = QFrame()
        status_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        status_layout = QGridLayout()
        status_group.setLayout(status_layout)

        status_header = QLabel("Mining Status")
        status_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        status_layout.addWidget(status_header, 0, 0, 1, 2)

        # Status Labels
        self.hashrate_label = QLabel("Hashrate: 0 MH/s")
        self.power_label = QLabel("Power: 0W")
        self.temp_label = QLabel("Temperature: 0°C")
        self.earnings_label = QLabel("Daily Earnings: $0.00")
        self.shares_label = QLabel("Shares: 0 / 0")
        self.uptime_label = QLabel("Uptime: 00:00:00")

        status_layout.addWidget(self.hashrate_label, 1, 0)
        status_layout.addWidget(self.power_label, 1, 1)
        status_layout.addWidget(self.temp_label, 2, 0)
        status_layout.addWidget(self.earnings_label, 2, 1)
        status_layout.addWidget(self.shares_label, 3, 0)
        status_layout.addWidget(self.uptime_label, 3, 1)

        layout.addWidget(status_group)

        # Hardware Info
        hardware_group = QFrame()
        hardware_group.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        hardware_layout = QVBoxLayout()
        hardware_group.setLayout(hardware_layout)

        hardware_header = QLabel("Hardware Information")
        hardware_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        hardware_layout.addWidget(hardware_header)

        self.hardware_text = QTextEdit()
        self.hardware_text.setReadOnly(True)
        hardware_layout.addWidget(self.hardware_text)

        layout.addWidget(hardware_group)

    def connect_wallet(self):
        address = self.wallet_address_input.text().strip()
        if not address:
            QMessageBox.warning(self, "Error", "Please enter a wallet address")
            return

        # For demo purposes, accept any non-empty address
        self.wallet_address = address
        self.wallet_address_input.setEnabled(False)
        self.connect_wallet_btn.setText("Connected")
        self.connect_wallet_btn.setEnabled(False)
        QMessageBox.information(self, "Success", "Wallet connected successfully!")

    def detect_hardware(self):
        # Hardware detection is now handled by HardwareMonitor
        pass

    def update_hardware_info(self, info):
        self.hardware_info = info
        self.update_hardware_display()

    def update_hardware_display(self):
        if not self.hardware_info:
            return

        text = "GPUs:\n"
        for gpu in self.hardware_info.get("gpus", []):
            text += f"- {gpu['name']}\n"
            text += f"  Memory: {gpu['memory']}GB\n"
            text += f"  Driver: {gpu['driver_version']}\n\n"

        text += "\nCPU:\n"
        cpu = self.hardware_info.get("cpu", {})
        text += f"- {cpu.get('name', 'Unknown')}\n"
        text += f"  Cores: {cpu.get('cores', 0)}\n"
        text += f"  Threads: {cpu.get('threads', 0)}\n"
        text += f"  Base Clock: {cpu.get('base_clock', 0)}GHz\n"

        text += f"\nTotal Memory: {self.hardware_info.get('total_memory', 0)}GB\n"
        text += f"Power Supply: {self.hardware_info.get('power_supply', 0)}W"

        self.hardware_text.setText(text)

    def start_mining(self):
        if not self.wallet_address:
            QMessageBox.warning(self, "Error", "Please connect your wallet first")
            return

        if self.mining_worker and self.mining_worker.isRunning():
            return

        # Create and start mining worker
        self.mining_worker = MiningWorker(
            self.wallet_address,
            self.coin_combo.currentText(),
            self.pool_combo.currentText()
        )
        self.mining_worker.status_update.connect(self.update_mining_status)
        self.mining_worker.error.connect(self.handle_mining_error)
        self.mining_worker.start()

        # Update UI
        self.start_mining_btn.setEnabled(False)
        self.stop_mining_btn.setEnabled(True)
        self.coin_combo.setEnabled(False)
        self.pool_combo.setEnabled(False)
        QMessageBox.information(self, "Success", "Mining started successfully!")

    def stop_mining(self):
        if self.mining_worker and self.mining_worker.isRunning():
            self.mining_worker.stop()
            self.mining_worker = None

            # Update UI
            self.start_mining_btn.setEnabled(True)
            self.stop_mining_btn.setEnabled(False)
            self.coin_combo.setEnabled(True)
            self.pool_combo.setEnabled(True)
            
            # Reset status
            self.hashrate_label.setText("Hashrate: 0 MH/s")
            self.power_label.setText("Power: 0W")
            self.temp_label.setText("Temperature: 0°C")
            self.shares_label.setText("Shares: 0 / 0")
            self.uptime_label.setText("Uptime: 00:00:00")
            self.boost_spinner.set_value(0)
            
            QMessageBox.information(self, "Success", "Mining stopped successfully!")

    def update_mining_status(self, status):
        self.mining_status = status
        
        # Update UI
        self.hashrate_label.setText(f"Hashrate: {status.get('hashrate', 0):.2f} MH/s")
        self.power_label.setText(f"Power: {status.get('power_consumption', 0):.1f}W")
        self.temp_label.setText(f"Temperature: {status.get('temperature', 0):.1f}°C")
        self.shares_label.setText(
            f"Shares: {status.get('accepted_shares', 0)} / {status.get('rejected_shares', 0)}"
        )
        self.uptime_label.setText(f"Uptime: {status.get('uptime', '00:00:00')}")
        
        # Update boost spinner
        efficiency = status.get('efficiency', 0)  # 0-100%
        self.boost_spinner.set_value(efficiency)
        
        # Calculate and update earnings (simplified calculation)
        if status.get('hashrate', 0) > 0:
            # Rough estimate: $0.1 per MH/s per day
            daily_earnings = status['hashrate'] * 0.1
            self.earnings_label.setText(f"Daily Earnings: ${daily_earnings:.2f}")

    def handle_mining_error(self, error_msg):
        QMessageBox.warning(self, "Mining Error", f"Error: {error_msg}")
        self.stop_mining()

    def closeEvent(self, event):
        # Stop mining and monitoring when closing
        if self.mining_worker:
            self.mining_worker.stop()
        if self.hardware_monitor:
            self.hardware_monitor.stop()
        super().closeEvent(event)

class ServerTab(QWidget):
    def __init__(self, game_name, game_key):
        super().__init__()
        self.game_name = game_name
        self.game_key = game_key
        self.current_subdir = ""
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # File browser area
        browser_layout = QHBoxLayout()
        
        # Left side - file list and navigation
        nav_layout = QVBoxLayout()
        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)
        
        self.path_label = QLabel("/")
        nav_layout.addWidget(self.path_label)
        
        nav_buttons = QHBoxLayout()
        self.up_btn = QPushButton("⬆️ Up")
        self.up_btn.clicked.connect(self.go_up)
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_file_list)
        nav_buttons.addWidget(self.up_btn)
        nav_buttons.addWidget(self.refresh_btn)
        nav_layout.addLayout(nav_buttons)
        
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.handle_item_double_click)
        nav_layout.addWidget(self.file_list)
        
        file_buttons = QHBoxLayout()
        self.new_file_btn = QPushButton("📄 New File")
        self.new_file_btn.clicked.connect(self.create_new_file)
        self.new_dir_btn = QPushButton("📁 New Dir")
        self.new_dir_btn.clicked.connect(self.create_new_directory)
        file_buttons.addWidget(self.new_file_btn)
        file_buttons.addWidget(self.new_dir_btn)
        nav_layout.addLayout(file_buttons)
        
        # Right side - editor
        editor_layout = QVBoxLayout()
        editor_widget = QWidget()
        editor_widget.setLayout(editor_layout)
        
        self.current_file_label = QLabel("No file open")
        editor_layout.addWidget(self.current_file_label)
        
        self.editor = QTextEdit()
        editor_layout.addWidget(self.editor)
        
        editor_buttons = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.save_file)
        self.save_btn.setEnabled(False)
        editor_buttons.addWidget(self.save_btn)
        editor_layout.addLayout(editor_buttons)
        
        # Add splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(nav_widget)
        splitter.addWidget(editor_widget)
        splitter.setSizes([200, 450])
        main_layout.addWidget(splitter)

        # AI chat area
        chat_layout = QVBoxLayout()
        chat_widget = QWidget()
        chat_widget.setLayout(chat_layout)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        chat_layout.addWidget(self.chat_display)
        
        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText(f"Ask {self.game_name} AI...")
        self.chat_input.returnPressed.connect(self.ask_ai)
        self.chat_send_btn = QPushButton("Ask AI")
        self.chat_send_btn.clicked.connect(self.ask_ai)
        chat_input_layout.addWidget(self.chat_input)
        chat_input_layout.addWidget(self.chat_send_btn)
        chat_layout.addLayout(chat_input_layout)
        
        main_layout.addWidget(chat_widget)

        self.refresh_file_list()
        self.refresh_status()

    def refresh_file_list(self):
        self.file_list.clear()
        try:
            resp = requests.post("http://localhost:8080/api/v1/list-files", json={"game": self.game_key, "subdir": self.current_subdir})
            if resp.status_code == 200:
                for item in resp.json().get("items", []):
                    name = item["name"]
                    if item["is_dir"]:
                        name += "/"
                    self.file_list.addItem(name)
        except Exception:
            self.file_list.addItem("[Error loading files]")

    def refresh_status(self):
        try:
            resp = requests.get("http://localhost:8080/api/v1/server-status", params={"game": self.game_key})
            if resp.status_code == 200:
                status = resp.json()
                self.status_label.setText(f"Status: {status['status']}")
                self.players_label.setText(f"Players: {status['players']}")
                self.uptime_label.setText(f"Uptime: {status['uptime']}")
        except Exception:
            pass

    def go_up(self):
        if "/" in self.current_subdir:
            self.current_subdir = self.current_subdir.rsplit("/", 1)[0]
        else:
            self.current_subdir = ""
        self.path_label.setText("/" + self.current_subdir)
        self.refresh_file_list()

    def handle_item_double_click(self, item):
        name = item.text()
        if name.endswith("/"):
            # Directory
            name = name[:-1]
        if self.current_subdir:
                self.current_subdir += "/" + name
            else:
                self.current_subdir = name
            self.path_label.setText("/" + self.current_subdir)
            self.refresh_file_list()
        else:
            # File
            try:
                path = f"{self.current_subdir}/{name}" if self.current_subdir else name
                resp = requests.get("http://localhost:8080/api/v1/read-file", 
                                  params={"game": self.game_key, "path": path})
                if resp.status_code == 200:
                    self.editor.setText(resp.json()["content"])
                    self.current_file_label.setText(path)
                    self.save_btn.setEnabled(True)
                else:
                    QMessageBox.warning(self, "Error", "Failed to read file")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def create_new_file(self):
        name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and name:
            try:
                path = f"{self.current_subdir}/{name}" if self.current_subdir else name
                resp = requests.post("http://localhost:8080/api/v1/create-file",
                                  json={"game": self.game_key, "path": path, "content": ""})
                if resp.status_code == 200:
            self.refresh_file_list()
                else:
                    QMessageBox.warning(self, "Error", "Failed to create file")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def create_new_directory(self):
        name, ok = QInputDialog.getText(self, "New Directory", "Enter directory name:")
        if ok and name:
            try:
                path = f"{self.current_subdir}/{name}" if self.current_subdir else name
                resp = requests.post("http://localhost:8080/api/v1/create-directory",
                                  json={"game": self.game_key, "path": path})
                if resp.status_code == 200:
                    self.refresh_file_list()
                else:
                    QMessageBox.warning(self, "Error", "Failed to create directory")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def save_file(self):
        try:
            path = self.current_file_label.text()
            if path != "No file open":
                resp = requests.post("http://localhost:8080/api/v1/write-file",
                                  json={"game": self.game_key, 
                                       "path": path,
                                       "content": self.editor.toPlainText()})
                if resp.status_code != 200:
                    QMessageBox.warning(self, "Error", "Failed to save file")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def ask_ai(self):
        query = self.chat_input.text()
        if query:
            self.chat_input.clear()
            self.chat_display.append(f"\nYou: {query}")
            try:
                resp = requests.post("http://localhost:8080/api/v1/chat",
                                  json={"game": self.game_key, "message": query})
                if resp.status_code == 200:
                    self.chat_display.append(f"\nAI: {resp.json()['response']}")
                else:
                    self.chat_display.append("\nAI: Sorry, I encountered an error.")
            except Exception:
                self.chat_display.append("\nAI: Sorry, I'm having trouble connecting.")
            self.chat_display.verticalScrollBar().setValue(
                self.chat_display.verticalScrollBar().maximum()
            )

class CreateServerWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Server - AI Wizard")
        self.setModal(True)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Game selection
        game_layout = QHBoxLayout()
        game_layout.addWidget(QLabel("Game:"))
        self.game_combo = QComboBox()
        for game_name, _ in SERVER_GAMES:
            self.game_combo.addItem(game_name)
        game_layout.addWidget(self.game_combo)
        layout.addLayout(game_layout)
        
        # AI chat
        self.chat_display = QTextBrowser()
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask the AI about server setup...")
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input)
        
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)
        
        # Buttons
        buttons = QHBoxLayout()
        create_btn = QPushButton("Create Server")
        create_btn.clicked.connect(self.create_server)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(create_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        # Start conversation
        self.chat_display.append("AI: Hi! I'll help you set up your game server. What would you like to know?")

    def send_message(self):
        message = self.chat_input.text()
        if message:
            self.chat_input.clear()
            self.chat_display.append(f"\nYou: {message}")
            try:
                game_key = SERVER_GAMES[self.game_combo.currentIndex()][1]
                resp = requests.post("http://localhost:8080/api/v1/server-wizard",
                                  json={"game": game_key, "message": message})
                if resp.status_code == 200:
                    self.chat_display.append(f"\nAI: {resp.json()['response']}")
                else:
                    self.chat_display.append("\nAI: Sorry, I encountered an error.")
            except Exception:
                self.chat_display.append("\nAI: Sorry, I'm having trouble connecting.")

    def create_server(self):
        try:
            game_key = SERVER_GAMES[self.game_combo.currentIndex()][1]
            resp = requests.post("http://localhost:8080/api/v1/create-server",
                              json={"game": game_key})
            if resp.status_code == 200:
                QMessageBox.information(self, "Success", "Server created successfully!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to create server")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CoresAI - Advanced AI Assistant")
        self.setGeometry(100, 100, 1200, 800)
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Header image
        header_label = QLabel()
        if os.path.exists(HEADER_IMAGE_PATH):
            pixmap = QPixmap(HEADER_IMAGE_PATH)
            header_label.setPixmap(pixmap.scaledToWidth(300, Qt.SmoothTransformation))
            header_label.setAlignment(Qt.AlignCenter)
        else:
            header_label.setText("CoresAI")
            header_label.setStyleSheet("font-size: 24px; font-weight: bold;")
            header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # Tabs
        self.tabs = QTabWidget()
        
        # Add Crypto Trading tab
        self.crypto_tab = CryptoTab()
        self.tabs.addTab(self.crypto_tab, "Crypto Trading")
        
        # Add Game Server tabs
        for game_name, game_key in SERVER_GAMES:
            self.tabs.addTab(ServerTab(game_name, game_key), game_name)
            
        layout.addWidget(self.tabs)

        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #3f3f3f;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3f3f3f;
                color: #ffffff;
                padding: 8px 20px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4f4f4f;
            }
            QFrame {
                background-color: #3f3f3f;
                border-radius: 5px;
                padding: 10px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #4f4f4f;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5f5f5f;
            }
            QPushButton:disabled {
                background-color: #3f3f3f;
                color: #7f7f7f;
            }
            QLineEdit {
                background-color: #4f4f4f;
                color: #ffffff;
                border: 1px solid #5f5f5f;
                padding: 5px;
                border-radius: 3px;
            }
            QTextEdit {
                background-color: #4f4f4f;
                color: #ffffff;
                border: 1px solid #5f5f5f;
                border-radius: 3px;
            }
            QComboBox {
                background-color: #4f4f4f;
                color: #ffffff;
                border: 1px solid #5f5f5f;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #4f4f4f;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMessageBox QPushButton {
                min-width: 80px;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Show splash screen
    if os.path.exists(SPLASH_IMAGE_PATH):
        splash_pix = QPixmap(SPLASH_IMAGE_PATH)
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.show()
        
        def show_main():
            window = MainWindow()
            window.show()
            splash.finish(window)
            
        QTimer.singleShot(SPLASH_DURATION, show_main)
    else:
        window = MainWindow()
        window.show()
    
    sys.exit(app.exec_()) 