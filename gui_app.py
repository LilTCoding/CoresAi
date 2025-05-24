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
    QTextBrowser, QProgressBar, QFrame, QScrollArea, QGridLayout, QSpinBox, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QGroupBox, QRadioButton, QCheckBox, QStackedWidget
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QFont, QIcon, QLinearGradient
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QPoint, QSize, QRect

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

# Styles
DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1a1a1a;
    color: #ffffff;
}

QTabWidget::pane {
    border: 1px solid #333333;
    background: #1a1a1a;
}

QTabBar::tab {
    background: #2d2d2d;
    color: #ffffff;
    padding: 8px 20px;
    border: 1px solid #333333;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background: #1a1a1a;
    border-bottom: none;
}

QPushButton {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #333333;
    padding: 5px 15px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #3d3d3d;
}

QPushButton:pressed {
    background-color: #404040;
}

QLineEdit, QTextEdit, QComboBox {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #333333;
    padding: 5px;
    border-radius: 4px;
}

QProgressBar {
    border: 1px solid #333333;
    border-radius: 4px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #00a8ff;
    border-radius: 3px;
}

QGroupBox {
    border: 1px solid #333333;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
    color: #00a8ff;
}

QLabel {
    color: #ffffff;
}

QTableWidget {
    background-color: #2d2d2d;
    color: #ffffff;
    gridline-color: #333333;
    border: 1px solid #333333;
    border-radius: 4px;
}

QTableWidget::item {
    padding: 5px;
}

QTableWidget::item:selected {
    background-color: #00a8ff;
}

QHeaderView::section {
    background-color: #2d2d2d;
    color: #ffffff;
    padding: 5px;
    border: 1px solid #333333;
}

QScrollBar:vertical {
    border: none;
    background: #2d2d2d;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #404040;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #2d2d2d;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #404040;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""

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
        self.mining_worker = None
        self.hardware_monitor = HardwareMonitor()
        self.hardware_monitor.hardware_update.connect(self.update_hardware_info)
        self.hardware_monitor.start()
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Hardware Info Section
        hardware_group = QGroupBox("Hardware Information")
        hardware_layout = QGridLayout()
        
        self.gpu_list = QTableWidget()
        self.gpu_list.setColumnCount(5)
        self.gpu_list.setHorizontalHeaderLabels(["GPU", "Memory", "Driver", "Core Clock", "Memory Clock"])
        hardware_layout.addWidget(self.gpu_list, 0, 0, 1, 2)
        
        self.cpu_info = QLabel("CPU: Detecting...")
        self.memory_info = QLabel("Memory: Detecting...")
        self.power_info = QLabel("Power Supply: Detecting...")
        
        hardware_layout.addWidget(self.cpu_info, 1, 0)
        hardware_layout.addWidget(self.memory_info, 1, 1)
        hardware_layout.addWidget(self.power_info, 2, 0, 1, 2)
        
        hardware_group.setLayout(hardware_layout)
        layout.addWidget(hardware_group)
        
        # Mining Controls Section
        mining_group = QGroupBox("Mining Controls")
        mining_layout = QGridLayout()
        
        # Wallet connection
        wallet_label = QLabel("Wallet Address:")
        self.wallet_input = QLineEdit()
        self.connect_wallet_btn = QPushButton("Connect Wallet")
        self.connect_wallet_btn.clicked.connect(self.connect_wallet)
        
        mining_layout.addWidget(wallet_label, 0, 0)
        mining_layout.addWidget(self.wallet_input, 0, 1)
        mining_layout.addWidget(self.connect_wallet_btn, 0, 2)
        
        # Coin selection
        coin_label = QLabel("Coin:")
        self.coin_combo = QComboBox()
        self.coin_combo.addItems(SUPPORTED_COINS)
        
        mining_layout.addWidget(coin_label, 1, 0)
        mining_layout.addWidget(self.coin_combo, 1, 1)
        
        # Pool selection
        pool_label = QLabel("Mining Pool:")
        self.pool_combo = QComboBox()
        self.pool_combo.addItems(MINING_POOLS)
        
        mining_layout.addWidget(pool_label, 2, 0)
        mining_layout.addWidget(self.pool_combo, 2, 1)
        
        # Mining controls
        self.start_mining_btn = QPushButton("Start Mining")
        self.start_mining_btn.clicked.connect(self.start_mining)
        self.stop_mining_btn = QPushButton("Stop Mining")
        self.stop_mining_btn.clicked.connect(self.stop_mining)
        self.stop_mining_btn.setEnabled(False)
        
        mining_layout.addWidget(self.start_mining_btn, 3, 0)
        mining_layout.addWidget(self.stop_mining_btn, 3, 1)
        
        mining_group.setLayout(mining_layout)
        layout.addWidget(mining_group)
        
        # Mining Status Section
        status_group = QGroupBox("Mining Status")
        status_layout = QGridLayout()
        
        self.hashrate_label = QLabel("Hashrate: 0 MH/s")
        self.shares_label = QLabel("Shares: 0 (0 accepted, 0 rejected)")
        self.earnings_label = QLabel("Estimated Earnings: 0.00 USD/day")
        self.power_usage_label = QLabel("Power Usage: 0W")
        self.temperature_label = QLabel("Temperature: 0°C")
        
        status_layout.addWidget(self.hashrate_label, 0, 0)
        status_layout.addWidget(self.shares_label, 0, 1)
        status_layout.addWidget(self.earnings_label, 1, 0)
        status_layout.addWidget(self.power_usage_label, 1, 1)
        status_layout.addWidget(self.temperature_label, 2, 0, 1, 2)
        
        # Progress bars
        self.hashrate_progress = QProgressBar()
        self.temperature_progress = QProgressBar()
        self.power_progress = QProgressBar()
        
        status_layout.addWidget(QLabel("Hashrate Utilization:"), 3, 0)
        status_layout.addWidget(self.hashrate_progress, 3, 1)
        status_layout.addWidget(QLabel("Temperature:"), 4, 0)
        status_layout.addWidget(self.temperature_progress, 4, 1)
        status_layout.addWidget(QLabel("Power Usage:"), 5, 0)
        status_layout.addWidget(self.power_progress, 5, 1)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Trading Section
        trading_group = QGroupBox("Trading")
        trading_layout = QGridLayout()
        
        # Market overview
        self.market_table = QTableWidget()
        self.market_table.setColumnCount(5)
        self.market_table.setHorizontalHeaderLabels(["Coin", "Price", "24h Change", "Volume", "Market Cap"])
        trading_layout.addWidget(self.market_table, 0, 0, 1, 4)
        
        # Trading controls
        amount_label = QLabel("Amount:")
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 1000000)
        self.amount_input.setDecimals(8)
        
        trading_layout.addWidget(amount_label, 1, 0)
        trading_layout.addWidget(self.amount_input, 1, 1)
        
        self.buy_btn = QPushButton("Buy")
        self.sell_btn = QPushButton("Sell")
        
        trading_layout.addWidget(self.buy_btn, 1, 2)
        trading_layout.addWidget(self.sell_btn, 1, 3)
        
        # Order book
        self.order_book = QTableWidget()
        self.order_book.setColumnCount(3)
        self.order_book.setHorizontalHeaderLabels(["Price", "Amount", "Total"])
        trading_layout.addWidget(self.order_book, 2, 0, 1, 4)
        
        trading_group.setLayout(trading_layout)
        layout.addWidget(trading_group)
        
    def connect_wallet(self):
        wallet_address = self.wallet_input.text().strip()
        if not wallet_address:
            QMessageBox.warning(self, "Error", "Please enter a wallet address")
            return
            
        try:
            # Validate wallet address format
            if not wallet_address.startswith("0x") or len(wallet_address) != 42:
                raise ValueError("Invalid wallet address format")
                
            self.wallet_input.setEnabled(False)
            self.connect_wallet_btn.setEnabled(False)
            self.start_mining_btn.setEnabled(True)
            QMessageBox.information(self, "Success", "Wallet connected successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect wallet: {str(e)}")
            
    def update_hardware_info(self, info):
        """Update hardware information display"""
        # Update GPU list
        self.gpu_list.setRowCount(len(info['gpus']))
        for i, gpu in enumerate(info['gpus']):
            self.gpu_list.setItem(i, 0, QTableWidgetItem(gpu['name']))
            self.gpu_list.setItem(i, 1, QTableWidgetItem(f"{gpu['memory']} GB"))
            self.gpu_list.setItem(i, 2, QTableWidgetItem(gpu['driver_version']))
            self.gpu_list.setItem(i, 3, QTableWidgetItem(f"{gpu['core_clock_mhz']} MHz"))
            self.gpu_list.setItem(i, 4, QTableWidgetItem(f"{gpu['memory_clock_mhz']} MHz"))
            
        # Update other hardware info
        if info['cpu']:
            self.cpu_info.setText(f"CPU: {info['cpu']['name']} ({info['cpu']['cores']} cores, {info['cpu']['threads']} threads)")
        self.memory_info.setText(f"Memory: {info['total_memory']} GB")
        self.power_info.setText(f"Estimated Power Supply: {info['power_supply']}W")
        
    def start_mining(self):
        """Start mining operation"""
        try:
            wallet = self.wallet_input.text().strip()
            coin = self.coin_combo.currentText()
            pool = self.pool_combo.currentText()
            
            self.mining_worker = MiningWorker(wallet, coin, pool)
            self.mining_worker.status_update.connect(self.update_mining_status)
            self.mining_worker.error.connect(self.handle_mining_error)
            self.mining_worker.start()
            
            self.start_mining_btn.setEnabled(False)
            self.stop_mining_btn.setEnabled(True)
            self.coin_combo.setEnabled(False)
            self.pool_combo.setEnabled(False)
            
            self.statusBar().showMessage("Mining started successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start mining: {str(e)}")
            
    def stop_mining(self):
        """Stop mining operation"""
        try:
            if self.mining_worker:
                self.mining_worker.stop()
                self.mining_worker = None
                
            self.start_mining_btn.setEnabled(True)
            self.stop_mining_btn.setEnabled(False)
            self.coin_combo.setEnabled(True)
            self.pool_combo.setEnabled(True)
            
            # Reset status displays
            self.hashrate_label.setText("Hashrate: 0 MH/s")
            self.shares_label.setText("Shares: 0 (0 accepted, 0 rejected)")
            self.earnings_label.setText("Estimated Earnings: 0.00 USD/day")
            self.power_usage_label.setText("Power Usage: 0W")
            self.temperature_label.setText("Temperature: 0°C")
            
            self.hashrate_progress.setValue(0)
            self.temperature_progress.setValue(0)
            self.power_progress.setValue(0)
            
            self.statusBar().showMessage("Mining stopped")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop mining: {str(e)}")
            
    def update_mining_status(self, status):
        """Update mining status display"""
        try:
            self.hashrate_label.setText(f"Hashrate: {status['hashrate']:.2f} MH/s")
            self.shares_label.setText(f"Shares: {status['total_shares']} ({status['accepted_shares']} accepted, {status['rejected_shares']} rejected)")
            self.earnings_label.setText(f"Estimated Earnings: {status['estimated_earnings']:.2f} USD/day")
            self.power_usage_label.setText(f"Power Usage: {status['power_usage']}W")
            self.temperature_label.setText(f"Temperature: {status['temperature']}°C")
            
            self.hashrate_progress.setValue(int(status['hashrate_percent']))
            self.temperature_progress.setValue(int(status['temperature_percent']))
            self.power_progress.setValue(int(status['power_percent']))
            
        except Exception as e:
            print(f"Error updating mining status: {str(e)}")
            
    def handle_mining_error(self, error_msg):
        """Handle mining errors"""
        QMessageBox.warning(self, "Mining Error", error_msg)
        self.stop_mining()
        
    def closeEvent(self, event):
        """Clean up when closing"""
        if self.mining_worker:
            self.stop_mining()
        if self.hardware_monitor:
            self.hardware_monitor.stop()
        event.accept()

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

class AIAssistantTab(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Chat interface
        chat_container = QWidget()
        chat_layout = QVBoxLayout()
        
        self.chat_display = QTextBrowser()
        self.chat_display.setMinimumHeight(400)
        
        input_container = QWidget()
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ask anything...")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_container.setLayout(input_layout)
        
        chat_layout.addWidget(self.chat_display)
        chat_layout.addWidget(input_container)
        chat_container.setLayout(chat_layout)
        
        layout.addWidget(chat_container)
        self.setLayout(layout)
        
    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            self.chat_display.append(f"You: {message}")
            self.message_input.clear()
            
            # Send to AI backend
            try:
                response = requests.post(f"{API_URL}/chat", json={
                    "messages": [{"role": "user", "content": message}]
                })
                if response.ok:
                    ai_response = response.json()["messages"][-1]["content"]
                    self.chat_display.append(f"AI: {ai_response}")
                else:
                    self.chat_display.append("AI: Sorry, I encountered an error. Please try again.")
            except Exception as e:
                self.chat_display.append(f"Error: {str(e)}")

class CryptoPoolTab(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Pool Overview Section
        overview_group = QGroupBox("Pool Overview")
        overview_layout = QGridLayout()
        
        # Pool selection
        pool_label = QLabel("Select Pool:")
        self.pool_combo = QComboBox()
        self.pool_combo.addItems(MINING_POOLS)
        self.pool_combo.currentTextChanged.connect(self.update_pool_info)
        
        overview_layout.addWidget(pool_label, 0, 0)
        overview_layout.addWidget(self.pool_combo, 0, 1)
        
        # Pool statistics
        self.hashrate_label = QLabel("Pool Hashrate: 0 TH/s")
        self.miners_label = QLabel("Active Miners: 0")
        self.blocks_label = QLabel("Blocks Found: 0")
        self.fee_label = QLabel("Pool Fee: 0%")
        
        overview_layout.addWidget(self.hashrate_label, 1, 0)
        overview_layout.addWidget(self.miners_label, 1, 1)
        overview_layout.addWidget(self.blocks_label, 2, 0)
        overview_layout.addWidget(self.fee_label, 2, 1)
        
        overview_group.setLayout(overview_layout)
        layout.addWidget(overview_group)
        
        # Worker Management Section
        workers_group = QGroupBox("Worker Management")
        workers_layout = QVBoxLayout()
        
        # Worker list
        self.worker_table = QTableWidget()
        self.worker_table.setColumnCount(6)
        self.worker_table.setHorizontalHeaderLabels([
            "Worker Name", "Hashrate", "Shares", "Efficiency",
            "Last Seen", "Status"
        ])
        workers_layout.addWidget(self.worker_table)
        
        # Worker controls
        controls_layout = QHBoxLayout()
        
        self.add_worker_btn = QPushButton("Add Worker")
        self.add_worker_btn.clicked.connect(self.add_worker)
        self.remove_worker_btn = QPushButton("Remove Worker")
        self.remove_worker_btn.clicked.connect(self.remove_worker)
        self.rename_worker_btn = QPushButton("Rename Worker")
        self.rename_worker_btn.clicked.connect(self.rename_worker)
        
        controls_layout.addWidget(self.add_worker_btn)
        controls_layout.addWidget(self.remove_worker_btn)
        controls_layout.addWidget(self.rename_worker_btn)
        
        workers_layout.addLayout(controls_layout)
        workers_group.setLayout(workers_layout)
        layout.addWidget(workers_group)
        
        # Payment History Section
        payments_group = QGroupBox("Payment History")
        payments_layout = QVBoxLayout()
        
        self.payment_table = QTableWidget()
        self.payment_table.setColumnCount(5)
        self.payment_table.setHorizontalHeaderLabels([
            "Date", "Amount", "Coin", "Transaction ID", "Status"
        ])
        payments_layout.addWidget(self.payment_table)
        
        # Payment settings
        settings_layout = QGridLayout()
        
        payout_label = QLabel("Minimum Payout:")
        self.payout_input = QDoubleSpinBox()
        self.payout_input.setRange(0.001, 1000)
        self.payout_input.setDecimals(6)
        self.payout_input.setValue(0.05)
        
        settings_layout.addWidget(payout_label, 0, 0)
        settings_layout.addWidget(self.payout_input, 0, 1)
        
        payment_method_label = QLabel("Payment Method:")
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["PPLNS", "PPS", "PPS+"])
        
        settings_layout.addWidget(payment_method_label, 1, 0)
        settings_layout.addWidget(self.payment_method_combo, 1, 1)
        
        self.auto_exchange_check = QCheckBox("Auto-exchange to BTC")
        settings_layout.addWidget(self.auto_exchange_check, 2, 0, 1, 2)
        
        self.save_settings_btn = QPushButton("Save Settings")
        self.save_settings_btn.clicked.connect(self.save_payment_settings)
        settings_layout.addWidget(self.save_settings_btn, 3, 0, 1, 2)
        
        payments_layout.addLayout(settings_layout)
        payments_group.setLayout(payments_layout)
        layout.addWidget(payments_group)
        
        # Start updating pool info
        self.update_pool_info()
        
    def update_pool_info(self):
        """Update pool information"""
        try:
            pool = self.pool_combo.currentText()
            # In a real implementation, this would fetch data from the pool's API
            # For now, we'll use dummy data
            self.hashrate_label.setText("Pool Hashrate: 1.5 TH/s")
            self.miners_label.setText("Active Miners: 1,234")
            self.blocks_label.setText("Blocks Found: 567")
            self.fee_label.setText("Pool Fee: 1%")
            
            # Update worker table with dummy data
            self.worker_table.setRowCount(3)
            workers = [
                ["Worker1", "45 MH/s", "123/2", "98%", "1 min ago", "Active"],
                ["Worker2", "62 MH/s", "234/1", "99%", "2 min ago", "Active"],
                ["Worker3", "0 MH/s", "0/0", "0%", "1 hour ago", "Offline"]
            ]
            for i, worker in enumerate(workers):
                for j, value in enumerate(worker):
                    self.worker_table.setItem(i, j, QTableWidgetItem(value))
                    
            # Update payment history with dummy data
            self.payment_table.setRowCount(3)
            payments = [
                ["2024-03-20", "0.1 ETH", "ETH", "0x123...abc", "Confirmed"],
                ["2024-03-19", "0.15 ETH", "ETH", "0x456...def", "Confirmed"],
                ["2024-03-18", "0.08 ETH", "ETH", "0x789...ghi", "Confirmed"]
            ]
            for i, payment in enumerate(payments):
                for j, value in enumerate(payment):
                    self.payment_table.setItem(i, j, QTableWidgetItem(value))
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update pool info: {str(e)}")
            
    def add_worker(self):
        """Add a new worker"""
        name, ok = QInputDialog.getText(self, "Add Worker", "Enter worker name:")
        if ok and name:
            try:
                row = self.worker_table.rowCount()
                self.worker_table.insertRow(row)
                self.worker_table.setItem(row, 0, QTableWidgetItem(name))
                self.worker_table.setItem(row, 1, QTableWidgetItem("0 MH/s"))
                self.worker_table.setItem(row, 2, QTableWidgetItem("0/0"))
                self.worker_table.setItem(row, 3, QTableWidgetItem("0%"))
                self.worker_table.setItem(row, 4, QTableWidgetItem("Just now"))
                self.worker_table.setItem(row, 5, QTableWidgetItem("Initializing"))
                QMessageBox.information(self, "Success", f"Worker '{name}' added successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add worker: {str(e)}")
                
    def remove_worker(self):
        """Remove selected worker"""
        current_row = self.worker_table.currentRow()
        if current_row >= 0:
            try:
                worker_name = self.worker_table.item(current_row, 0).text()
                reply = QMessageBox.question(
                    self, "Confirm Removal",
                    f"Are you sure you want to remove worker '{worker_name}'?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.worker_table.removeRow(current_row)
                    QMessageBox.information(self, "Success", f"Worker '{worker_name}' removed successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove worker: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Please select a worker to remove")
            
    def rename_worker(self):
        """Rename selected worker"""
        current_row = self.worker_table.currentRow()
        if current_row >= 0:
            try:
                old_name = self.worker_table.item(current_row, 0).text()
                new_name, ok = QInputDialog.getText(
                    self, "Rename Worker",
                    f"Enter new name for worker '{old_name}':"
                )
                if ok and new_name:
                    self.worker_table.setItem(current_row, 0, QTableWidgetItem(new_name))
                    QMessageBox.information(self, "Success", f"Worker renamed from '{old_name}' to '{new_name}'")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to rename worker: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Please select a worker to rename")
            
    def save_payment_settings(self):
        """Save payment settings"""
        try:
            settings = {
                "minimum_payout": self.payout_input.value(),
                "payment_method": self.payment_method_combo.currentText(),
                "auto_exchange": self.auto_exchange_check.isChecked()
            }
            # In a real implementation, this would save to a config file or API
            QMessageBox.information(self, "Success", "Payment settings saved successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save payment settings: {str(e)}")

class FriendTrackingTab(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Friend List Section
        friends_group = QGroupBox("Friends")
        friends_layout = QVBoxLayout()
        
        # Search and filter
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search friends...")
        self.search_input.textChanged.connect(self.filter_friends)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Online", "Offline", "Mining", "Gaming"])
        self.status_filter.currentTextChanged.connect(self.filter_friends)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.status_filter)
        friends_layout.addLayout(search_layout)
        
        # Friend list table
        self.friend_table = QTableWidget()
        self.friend_table.setColumnCount(6)
        self.friend_table.setHorizontalHeaderLabels([
            "Username", "Status", "Activity",
            "Mining Power", "Earnings", "Last Seen"
        ])
        friends_layout.addWidget(self.friend_table)
        
        # Friend controls
        controls_layout = QHBoxLayout()
        
        self.add_friend_btn = QPushButton("Add Friend")
        self.add_friend_btn.clicked.connect(self.add_friend)
        self.remove_friend_btn = QPushButton("Remove Friend")
        self.remove_friend_btn.clicked.connect(self.remove_friend)
        self.message_friend_btn = QPushButton("Message")
        self.message_friend_btn.clicked.connect(self.message_friend)
        
        controls_layout.addWidget(self.add_friend_btn)
        controls_layout.addWidget(self.remove_friend_btn)
        controls_layout.addWidget(self.message_friend_btn)
        
        friends_layout.addLayout(controls_layout)
        friends_group.setLayout(friends_layout)
        layout.addWidget(friends_group)
        
        # Activity Feed Section
        activity_group = QGroupBox("Activity Feed")
        activity_layout = QVBoxLayout()
        
        self.activity_list = QTextBrowser()
        self.activity_list.setMinimumHeight(150)
        activity_layout.addWidget(self.activity_list)
        
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        # Mining Pool Section
        pool_group = QGroupBox("Mining Pool")
        pool_layout = QGridLayout()
        
        # Pool statistics
        self.pool_size_label = QLabel("Pool Size: 0 members")
        self.pool_hashrate_label = QLabel("Total Hashrate: 0 MH/s")
        self.pool_earnings_label = QLabel("Pool Earnings: 0 ETH")
        
        pool_layout.addWidget(self.pool_size_label, 0, 0)
        pool_layout.addWidget(self.pool_hashrate_label, 0, 1)
        pool_layout.addWidget(self.pool_earnings_label, 1, 0, 1, 2)
        
        # Pool controls
        self.create_pool_btn = QPushButton("Create Pool")
        self.create_pool_btn.clicked.connect(self.create_pool)
        self.invite_friend_btn = QPushButton("Invite Friend")
        self.invite_friend_btn.clicked.connect(self.invite_to_pool)
        
        pool_layout.addWidget(self.create_pool_btn, 2, 0)
        pool_layout.addWidget(self.invite_friend_btn, 2, 1)
        
        pool_group.setLayout(pool_layout)
        layout.addWidget(pool_group)
        
        # Initialize with dummy data
        self.load_dummy_data()
        
    def load_dummy_data(self):
        """Load dummy data for demonstration"""
        # Add dummy friends
        self.friend_table.setRowCount(4)
        friends = [
            ["CryptoMaster", "Online", "Mining ETH", "120 MH/s", "0.5 ETH", "Now"],
            ["GameKing", "Online", "Playing Rust", "0 MH/s", "0.2 ETH", "Now"],
            ["MiningPro", "Offline", "Idle", "0 MH/s", "1.2 ETH", "2 hours ago"],
            ["TechGuru", "Online", "Mining RVN", "85 MH/s", "0.8 ETH", "Now"]
        ]
        for i, friend in enumerate(friends):
            for j, value in enumerate(friend):
                self.friend_table.setItem(i, j, QTableWidgetItem(value))
                
        # Add dummy activity feed
        activities = [
            "CryptoMaster started mining ETH - 2 minutes ago",
            "GameKing joined Rust server 'Alpha' - 15 minutes ago",
            "TechGuru achieved mining milestone: 1000 shares - 1 hour ago",
            "MiningPro went offline - 2 hours ago",
            "Pool 'Alpha Miners' distributed 0.5 ETH rewards - 3 hours ago"
        ]
        self.activity_list.setText("\n\n".join(activities))
        
    def filter_friends(self):
        """Filter friends list based on search and status"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()
        
        for row in range(self.friend_table.rowCount()):
            username = self.friend_table.item(row, 0).text().lower()
            status = self.friend_table.item(row, 1).text()
            
            show_row = True
            if search_text and search_text not in username:
                show_row = False
            if status_filter != "All" and status_filter != status:
                show_row = False
                
            self.friend_table.setRowHidden(row, not show_row)
            
    def add_friend(self):
        """Add a new friend"""
        username, ok = QInputDialog.getText(self, "Add Friend", "Enter friend's username:")
        if ok and username:
            try:
                row = self.friend_table.rowCount()
                self.friend_table.insertRow(row)
                self.friend_table.setItem(row, 0, QTableWidgetItem(username))
                self.friend_table.setItem(row, 1, QTableWidgetItem("Offline"))
                self.friend_table.setItem(row, 2, QTableWidgetItem("Idle"))
                self.friend_table.setItem(row, 3, QTableWidgetItem("0 MH/s"))
                self.friend_table.setItem(row, 4, QTableWidgetItem("0 ETH"))
                self.friend_table.setItem(row, 5, QTableWidgetItem("Just added"))
                
                self.activity_list.append(f"\n\nAdded new friend: {username}")
                QMessageBox.information(self, "Success", f"Friend '{username}' added successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add friend: {str(e)}")
                
    def remove_friend(self):
        """Remove selected friend"""
        current_row = self.friend_table.currentRow()
        if current_row >= 0:
            try:
                username = self.friend_table.item(current_row, 0).text()
                reply = QMessageBox.question(
                    self, "Confirm Removal",
                    f"Are you sure you want to remove friend '{username}'?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.friend_table.removeRow(current_row)
                    self.activity_list.append(f"\n\nRemoved friend: {username}")
                    QMessageBox.information(self, "Success", f"Friend '{username}' removed successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove friend: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Please select a friend to remove")
            
    def message_friend(self):
        """Send message to selected friend"""
        current_row = self.friend_table.currentRow()
        if current_row >= 0:
            try:
                username = self.friend_table.item(current_row, 0).text()
                message, ok = QInputDialog.getText(
                    self, "Send Message",
                    f"Enter message for {username}:"
                )
                if ok and message:
                    self.activity_list.append(f"\n\nSent message to {username}: {message}")
                    QMessageBox.information(self, "Success", f"Message sent to {username}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to send message: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Please select a friend to message")
            
    def create_pool(self):
        """Create a new mining pool"""
        name, ok = QInputDialog.getText(self, "Create Pool", "Enter pool name:")
        if ok and name:
            try:
                self.pool_size_label.setText("Pool Size: 1 member")
                self.pool_hashrate_label.setText("Total Hashrate: 0 MH/s")
                self.pool_earnings_label.setText("Pool Earnings: 0 ETH")
                
                self.create_pool_btn.setEnabled(False)
                self.invite_friend_btn.setEnabled(True)
                
                self.activity_list.append(f"\n\nCreated new mining pool: {name}")
                QMessageBox.information(self, "Success", f"Pool '{name}' created successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create pool: {str(e)}")
                
    def invite_to_pool(self):
        """Invite selected friend to pool"""
        current_row = self.friend_table.currentRow()
        if current_row >= 0:
            try:
                username = self.friend_table.item(current_row, 0).text()
                self.activity_list.append(f"\n\nInvited {username} to join the pool")
                QMessageBox.information(self, "Success", f"Invitation sent to {username}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to send invitation: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Please select a friend to invite")

class PortfolioTab(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Portfolio Overview Section
        overview_group = QGroupBox("Portfolio Overview")
        overview_layout = QGridLayout()
        
        # Total value
        self.total_value_label = QLabel("Total Value: $0.00")
        self.total_value_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        overview_layout.addWidget(self.total_value_label, 0, 0, 1, 2)
        
        # Performance metrics
        self.daily_change_label = QLabel("24h Change: +0.00%")
        self.weekly_change_label = QLabel("7d Change: +0.00%")
        self.monthly_change_label = QLabel("30d Change: +0.00%")
        
        overview_layout.addWidget(self.daily_change_label, 1, 0)
        overview_layout.addWidget(self.weekly_change_label, 1, 1)
        overview_layout.addWidget(self.monthly_change_label, 2, 0, 1, 2)
        
        overview_group.setLayout(overview_layout)
        layout.addWidget(overview_group)
        
        # Asset Distribution Section
        assets_group = QGroupBox("Asset Distribution")
        assets_layout = QVBoxLayout()
        
        self.asset_table = QTableWidget()
        self.asset_table.setColumnCount(7)
        self.asset_table.setHorizontalHeaderLabels([
            "Asset", "Amount", "Price", "Value",
            "24h Change", "7d Change", "Weight"
        ])
        assets_layout.addWidget(self.asset_table)
        
        # Asset controls
        controls_layout = QHBoxLayout()
        
        self.add_asset_btn = QPushButton("Add Asset")
        self.add_asset_btn.clicked.connect(self.add_asset)
        self.remove_asset_btn = QPushButton("Remove Asset")
        self.remove_asset_btn.clicked.connect(self.remove_asset)
        self.edit_asset_btn = QPushButton("Edit Asset")
        self.edit_asset_btn.clicked.connect(self.edit_asset)
        
        controls_layout.addWidget(self.add_asset_btn)
        controls_layout.addWidget(self.remove_asset_btn)
        controls_layout.addWidget(self.edit_asset_btn)
        
        assets_layout.addLayout(controls_layout)
        assets_group.setLayout(assets_layout)
        layout.addWidget(assets_group)
        
        # Transaction History Section
        transactions_group = QGroupBox("Transaction History")
        transactions_layout = QVBoxLayout()
        
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(7)
        self.transaction_table.setHorizontalHeaderLabels([
            "Date", "Type", "Asset", "Amount",
            "Price", "Value", "Status"
        ])
        transactions_layout.addWidget(self.transaction_table)
        
        # Transaction controls
        transaction_controls = QHBoxLayout()
        
        self.add_transaction_btn = QPushButton("Add Transaction")
        self.add_transaction_btn.clicked.connect(self.add_transaction)
        self.export_history_btn = QPushButton("Export History")
        self.export_history_btn.clicked.connect(self.export_history)
        
        transaction_controls.addWidget(self.add_transaction_btn)
        transaction_controls.addWidget(self.export_history_btn)
        
        transactions_layout.addLayout(transaction_controls)
        transactions_group.setLayout(transactions_layout)
        layout.addWidget(transactions_group)
        
        # AI Insights Section
        insights_group = QGroupBox("AI Insights")
        insights_layout = QVBoxLayout()
        
        self.insights_text = QTextBrowser()
        self.insights_text.setMinimumHeight(100)
        insights_layout.addWidget(self.insights_text)
        
        # Refresh insights button
        self.refresh_insights_btn = QPushButton("Refresh Insights")
        self.refresh_insights_btn.clicked.connect(self.refresh_insights)
        insights_layout.addWidget(self.refresh_insights_btn)
        
        insights_group.setLayout(insights_layout)
        layout.addWidget(insights_group)
        
        # Initialize with dummy data
        self.load_dummy_data()
        
    def load_dummy_data(self):
        """Load dummy data for demonstration"""
        # Update overview
        self.total_value_label.setText("Total Value: $25,750.00")
        self.daily_change_label.setText("24h Change: +2.5%")
        self.weekly_change_label.setText("7d Change: +8.3%")
        self.monthly_change_label.setText("30d Change: +15.7%")
        
        # Add dummy assets
        self.asset_table.setRowCount(4)
        assets = [
            ["BTC", "0.5", "$40,000", "$20,000", "+3.2%", "+10.5%", "77.7%"],
            ["ETH", "2.5", "$2,000", "$5,000", "+1.8%", "+5.2%", "19.4%"],
            ["XMR", "5.0", "$100", "$500", "-0.5%", "+2.1%", "1.9%"],
            ["RVN", "1000", "$0.25", "$250", "+5.2%", "+15.3%", "1.0%"]
        ]
        for i, asset in enumerate(assets):
            for j, value in enumerate(asset):
                self.asset_table.setItem(i, j, QTableWidgetItem(value))
                
        # Add dummy transactions
        self.transaction_table.setRowCount(4)
        transactions = [
            ["2024-03-20", "Buy", "BTC", "0.1", "$39,500", "$3,950", "Completed"],
            ["2024-03-19", "Sell", "ETH", "1.0", "$2,100", "$2,100", "Completed"],
            ["2024-03-18", "Buy", "XMR", "2.0", "$98", "$196", "Completed"],
            ["2024-03-17", "Mining", "RVN", "100", "$0.24", "$24", "Completed"]
        ]
        for i, transaction in enumerate(transactions):
            for j, value in enumerate(transaction):
                self.transaction_table.setItem(i, j, QTableWidgetItem(value))
                
        # Add dummy insights
        insights = [
            "Portfolio Diversification: Well balanced between major and alt coins",
            "Risk Analysis: Moderate risk profile with 77.7% in BTC",
            "Recommendation: Consider increasing ETH position given recent market trends",
            "Mining Revenue: RVN mining showing positive ROI in the last 30 days"
        ]
        self.insights_text.setText("\n\n".join(insights))
        
    def add_asset(self):
        """Add a new asset to portfolio"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Add Asset")
            layout = QGridLayout()
            
            # Asset inputs
            layout.addWidget(QLabel("Asset:"), 0, 0)
            asset_input = QComboBox()
            asset_input.addItems(SUPPORTED_COINS)
            layout.addWidget(asset_input, 0, 1)
            
            layout.addWidget(QLabel("Amount:"), 1, 0)
            amount_input = QDoubleSpinBox()
            amount_input.setRange(0, 1000000)
            amount_input.setDecimals(8)
            layout.addWidget(amount_input, 1, 1)
            
            # Buttons
            buttons = QHBoxLayout()
            ok_btn = QPushButton("Add")
            cancel_btn = QPushButton("Cancel")
            buttons.addWidget(ok_btn)
            buttons.addWidget(cancel_btn)
            layout.addLayout(buttons, 2, 0, 1, 2)
            
            dialog.setLayout(layout)
            
            ok_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            if dialog.exec_() == QDialog.Accepted:
                asset = asset_input.currentText()
                amount = amount_input.value()
                
                row = self.asset_table.rowCount()
                self.asset_table.insertRow(row)
                self.asset_table.setItem(row, 0, QTableWidgetItem(asset))
                self.asset_table.setItem(row, 1, QTableWidgetItem(str(amount)))
                self.asset_table.setItem(row, 2, QTableWidgetItem("$0.00"))
                self.asset_table.setItem(row, 3, QTableWidgetItem("$0.00"))
                self.asset_table.setItem(row, 4, QTableWidgetItem("0.00%"))
                self.asset_table.setItem(row, 5, QTableWidgetItem("0.00%"))
                self.asset_table.setItem(row, 6, QTableWidgetItem("0.00%"))
                
                QMessageBox.information(self, "Success", f"Added {amount} {asset} to portfolio")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add asset: {str(e)}")
            
    def remove_asset(self):
        """Remove selected asset"""
        current_row = self.asset_table.currentRow()
        if current_row >= 0:
            try:
                asset = self.asset_table.item(current_row, 0).text()
                amount = self.asset_table.item(current_row, 1).text()
                reply = QMessageBox.question(
                    self, "Confirm Removal",
                    f"Are you sure you want to remove {amount} {asset}?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.asset_table.removeRow(current_row)
                    QMessageBox.information(self, "Success", f"Removed {amount} {asset} from portfolio")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove asset: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Please select an asset to remove")
            
    def edit_asset(self):
        """Edit selected asset"""
        current_row = self.asset_table.currentRow()
        if current_row >= 0:
            try:
                asset = self.asset_table.item(current_row, 0).text()
                old_amount = float(self.asset_table.item(current_row, 1).text())
                
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Edit {asset}")
                layout = QGridLayout()
                
                layout.addWidget(QLabel("New Amount:"), 0, 0)
                amount_input = QDoubleSpinBox()
                amount_input.setRange(0, 1000000)
                amount_input.setDecimals(8)
                amount_input.setValue(old_amount)
                layout.addWidget(amount_input, 0, 1)
                
                buttons = QHBoxLayout()
                ok_btn = QPushButton("Save")
                cancel_btn = QPushButton("Cancel")
                buttons.addWidget(ok_btn)
                buttons.addWidget(cancel_btn)
                layout.addLayout(buttons, 1, 0, 1, 2)
                
                dialog.setLayout(layout)
                
                ok_btn.clicked.connect(dialog.accept)
                cancel_btn.clicked.connect(dialog.reject)
                
                if dialog.exec_() == QDialog.Accepted:
                    new_amount = amount_input.value()
                    self.asset_table.setItem(current_row, 1, QTableWidgetItem(str(new_amount)))
                    QMessageBox.information(
                        self, "Success",
                        f"Updated {asset} amount from {old_amount} to {new_amount}"
                    )
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to edit asset: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Please select an asset to edit")
            
    def add_transaction(self):
        """Add a new transaction"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Add Transaction")
            layout = QGridLayout()
            
            # Transaction inputs
            layout.addWidget(QLabel("Type:"), 0, 0)
            type_input = QComboBox()
            type_input.addItems(["Buy", "Sell", "Mining", "Transfer"])
            layout.addWidget(type_input, 0, 1)
            
            layout.addWidget(QLabel("Asset:"), 1, 0)
            asset_input = QComboBox()
            asset_input.addItems(SUPPORTED_COINS)
            layout.addWidget(asset_input, 1, 1)
            
            layout.addWidget(QLabel("Amount:"), 2, 0)
            amount_input = QDoubleSpinBox()
            amount_input.setRange(0, 1000000)
            amount_input.setDecimals(8)
            layout.addWidget(amount_input, 2, 1)
            
            layout.addWidget(QLabel("Price:"), 3, 0)
            price_input = QDoubleSpinBox()
            price_input.setRange(0, 1000000)
            price_input.setDecimals(2)
            price_input.setPrefix("$")
            layout.addWidget(price_input, 3, 1)
            
            # Buttons
            buttons = QHBoxLayout()
            ok_btn = QPushButton("Add")
            cancel_btn = QPushButton("Cancel")
            buttons.addWidget(ok_btn)
            buttons.addWidget(cancel_btn)
            layout.addLayout(buttons, 4, 0, 1, 2)
            
            dialog.setLayout(layout)
            
            ok_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            if dialog.exec_() == QDialog.Accepted:
                tx_type = type_input.currentText()
                asset = asset_input.currentText()
                amount = amount_input.value()
                price = price_input.value()
                value = amount * price
                
                row = self.transaction_table.rowCount()
                self.transaction_table.insertRow(row)
                self.transaction_table.setItem(row, 0, QTableWidgetItem(datetime.now().strftime("%Y-%m-%d")))
                self.transaction_table.setItem(row, 1, QTableWidgetItem(tx_type))
                self.transaction_table.setItem(row, 2, QTableWidgetItem(asset))
                self.transaction_table.setItem(row, 3, QTableWidgetItem(str(amount)))
                self.transaction_table.setItem(row, 4, QTableWidgetItem(f"${price:.2f}"))
                self.transaction_table.setItem(row, 5, QTableWidgetItem(f"${value:.2f}"))
                self.transaction_table.setItem(row, 6, QTableWidgetItem("Completed"))
                
                QMessageBox.information(
                    self, "Success",
                    f"Added {tx_type} transaction: {amount} {asset} at ${price:.2f}"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add transaction: {str(e)}")
            
    def export_history(self):
        """Export transaction history to CSV"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Transaction History",
                "transaction_history.csv",
                "CSV Files (*.csv)"
            )
            if filename:
                with open(filename, 'w') as f:
                    # Write header
                    headers = []
                    for i in range(self.transaction_table.columnCount()):
                        headers.append(self.transaction_table.horizontalHeaderItem(i).text())
                    f.write(",".join(headers) + "\n")
                    
                    # Write data
                    for row in range(self.transaction_table.rowCount()):
                        row_data = []
                        for col in range(self.transaction_table.columnCount()):
                            item = self.transaction_table.item(row, col)
                            row_data.append(item.text() if item else "")
                        f.write(",".join(row_data) + "\n")
                        
                QMessageBox.information(
                    self, "Success",
                    f"Transaction history exported to {filename}"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export history: {str(e)}")
            
    def refresh_insights(self):
        """Refresh AI insights"""
        try:
            # In a real implementation, this would call an AI service
            insights = [
                "Portfolio Analysis:",
                "- Strong Bitcoin position (77.7%) provides stability",
                "- Ethereum allocation (19.4%) aligns with market trends",
                "- Privacy coins (XMR) offer good diversification",
                "",
                "Recommendations:",
                "- Consider taking profits on RVN after recent 15.3% gain",
                "- Watch for ETH 2.0 staking opportunities",
                "- Monitor BTC dominance for potential altcoin season"
            ]
            self.insights_text.setText("\n".join(insights))
            QMessageBox.information(self, "Success", "AI insights updated successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh insights: {str(e)}")

class FiveMAntiCheatTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_anticheat = None
        self.blacklisted_props = []
        self.blacklisted_weapons = []
        self.blacklisted_vehicles = []
        self.blacklisted_peds = []
        self.blacklisted_words = []
        self.blacklisted_explosions = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Anticheat selection and basic config
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Anticheat Selection
        selection_group = QGroupBox("Anticheat Selection")
        selection_layout = QVBoxLayout()
        
        self.anticheat_combo = QComboBox()
        self.anticheat_combo.addItems(["Badger Anticheat", "WaveShield", "Dub Anticheat"])
        self.anticheat_combo.currentTextChanged.connect(self.load_anticheat_config)
        selection_layout.addWidget(self.anticheat_combo)
        
        selection_group.setLayout(selection_layout)
        left_layout.addWidget(selection_group)
        
        # Basic Configuration
        config_group = QGroupBox("Basic Configuration")
        config_layout = QVBoxLayout()
        
        # Components toggle
        components_label = QLabel("Protection Components:")
        config_layout.addWidget(components_label)
        
        self.noclip_check = QCheckBox("Anti NoClip")
        self.spectate_check = QCheckBox("Anti Spectate")
        self.chat_check = QCheckBox("Anti Fake Chat")
        self.props_check = QCheckBox("Anti Blacklisted Props")
        self.resource_check = QCheckBox("Resource Protection")
        self.injection_check = QCheckBox("Anti Injection")
        self.vpn_check = QCheckBox("Anti VPN")
        self.explosion_check = QCheckBox("Explosion Protection")
        self.weapon_check = QCheckBox("Weapon Protection")
        
        config_layout.addWidget(self.noclip_check)
        config_layout.addWidget(self.spectate_check)
        config_layout.addWidget(self.chat_check)
        config_layout.addWidget(self.props_check)
        config_layout.addWidget(self.resource_check)
        config_layout.addWidget(self.injection_check)
        config_layout.addWidget(self.vpn_check)
        config_layout.addWidget(self.explosion_check)
        config_layout.addWidget(self.weapon_check)
        
        config_group.setLayout(config_layout)
        left_layout.addWidget(config_group)
        
        # Discord Integration
        discord_group = QGroupBox("Discord Integration")
        discord_layout = QGridLayout()
        
        discord_layout.addWidget(QLabel("Webhook URL:"), 0, 0)
        self.webhook_input = QLineEdit()
        discord_layout.addWidget(self.webhook_input, 0, 1)
        
        self.log_detections = QCheckBox("Log Detections")
        self.log_kicks = QCheckBox("Log Kicks")
        self.log_bans = QCheckBox("Log Bans")
        
        discord_layout.addWidget(self.log_detections, 1, 0)
        discord_layout.addWidget(self.log_kicks, 1, 1)
        discord_layout.addWidget(self.log_bans, 2, 0)
        
        discord_group.setLayout(discord_layout)
        left_layout.addWidget(discord_group)
        
        splitter.addWidget(left_widget)
        
        # Right side - Advanced configuration tabs
        right_widget = QTabWidget()
        
        # Blacklist Management Tab
        blacklist_tab = QWidget()
        blacklist_layout = QVBoxLayout(blacklist_tab)
        
        # Props Blacklist
        props_group = QGroupBox("Blacklisted Props")
        props_layout = QVBoxLayout()
        
        self.props_list = QListWidget()
        props_layout.addWidget(self.props_list)
        
        props_buttons = QHBoxLayout()
        self.add_prop_btn = QPushButton("Add Prop")
        self.remove_prop_btn = QPushButton("Remove Prop")
        self.add_prop_btn.clicked.connect(lambda: self.add_blacklist_item("prop"))
        self.remove_prop_btn.clicked.connect(lambda: self.remove_blacklist_item("prop"))
        props_buttons.addWidget(self.add_prop_btn)
        props_buttons.addWidget(self.remove_prop_btn)
        props_layout.addLayout(props_buttons)
        
        props_group.setLayout(props_layout)
        blacklist_layout.addWidget(props_group)
        
        # Weapons Blacklist
        weapons_group = QGroupBox("Blacklisted Weapons")
        weapons_layout = QVBoxLayout()
        
        self.weapons_list = QListWidget()
        weapons_layout.addWidget(self.weapons_list)
        
        weapons_buttons = QHBoxLayout()
        self.add_weapon_btn = QPushButton("Add Weapon")
        self.remove_weapon_btn = QPushButton("Remove Weapon")
        self.add_weapon_btn.clicked.connect(lambda: self.add_blacklist_item("weapon"))
        self.remove_weapon_btn.clicked.connect(lambda: self.remove_blacklist_item("weapon"))
        weapons_buttons.addWidget(self.add_weapon_btn)
        weapons_buttons.addWidget(self.remove_weapon_btn)
        weapons_layout.addLayout(weapons_buttons)
        
        weapons_group.setLayout(weapons_layout)
        blacklist_layout.addWidget(weapons_group)
        
        right_widget.addTab(blacklist_tab, "Blacklists")
        
        # Detection Rules Tab
        rules_tab = QWidget()
        rules_layout = QVBoxLayout(rules_tab)
        
        # NoClip Detection
        noclip_group = QGroupBox("NoClip Detection")
        noclip_layout = QGridLayout()
        
        noclip_layout.addWidget(QLabel("Trigger Count:"), 0, 0)
        self.noclip_count = QSpinBox()
        self.noclip_count.setValue(3)
        noclip_layout.addWidget(self.noclip_count, 0, 1)
        
        noclip_layout.addWidget(QLabel("Action:"), 1, 0)
        self.noclip_action = QComboBox()
        self.noclip_action.addItems(["Kick", "Ban", "Log Only"])
        noclip_layout.addWidget(self.noclip_action, 1, 1)
        
        noclip_group.setLayout(noclip_layout)
        rules_layout.addWidget(noclip_group)
        
        # Weapon Detection
        weapon_group = QGroupBox("Weapon Detection")
        weapon_layout = QGridLayout()
        
        self.weapon_damage_check = QCheckBox("Detect Damage Modification")
        self.weapon_explosive_check = QCheckBox("Detect Explosive Ammo")
        self.weapon_infinite_check = QCheckBox("Detect Infinite Ammo")
        
        weapon_layout.addWidget(self.weapon_damage_check, 0, 0)
        weapon_layout.addWidget(self.weapon_explosive_check, 1, 0)
        weapon_layout.addWidget(self.weapon_infinite_check, 2, 0)
        
        weapon_group.setLayout(weapon_layout)
        rules_layout.addWidget(weapon_group)
        
        right_widget.addTab(rules_tab, "Detection Rules")
        
        # Ban Management Tab
        ban_tab = QWidget()
        ban_layout = QVBoxLayout(ban_tab)
        
        self.ban_table = QTableWidget()
        self.ban_table.setColumnCount(5)
        self.ban_table.setHorizontalHeaderLabels([
            "Player", "Steam ID", "Reason", "Date", "Actions"
        ])
        ban_layout.addWidget(self.ban_table)
        
        ban_buttons = QHBoxLayout()
        self.add_ban_btn = QPushButton("Add Ban")
        self.remove_ban_btn = QPushButton("Remove Ban")
        self.export_bans_btn = QPushButton("Export Bans")
        
        self.add_ban_btn.clicked.connect(self.add_ban)
        self.remove_ban_btn.clicked.connect(self.remove_ban)
        self.export_bans_btn.clicked.connect(self.export_bans)
        
        ban_buttons.addWidget(self.add_ban_btn)
        ban_buttons.addWidget(self.remove_ban_btn)
        ban_buttons.addWidget(self.export_bans_btn)
        
        ban_layout.addLayout(ban_buttons)
        right_widget.addTab(ban_tab, "Ban Management")
        
        splitter.addWidget(right_widget)
        layout.addWidget(splitter)
        
        # Bottom buttons
        buttons_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Configuration")
        self.apply_btn = QPushButton("Apply Configuration")
        self.export_btn = QPushButton("Export Configuration")
        
        self.save_btn.clicked.connect(self.save_config)
        self.apply_btn.clicked.connect(self.apply_config)
        self.export_btn.clicked.connect(self.export_config)
        
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.apply_btn)
        buttons_layout.addWidget(self.export_btn)
        
        layout.addLayout(buttons_layout)
        
        # Initialize with default anticheat
        self.load_anticheat_config("Badger Anticheat")
        
    def load_anticheat_config(self, anticheat_name):
        """Load configuration for selected anticheat"""
        try:
            self.current_anticheat = anticheat_name
            
            if anticheat_name == "Badger Anticheat":
                # Load Badger anticheat config
                self.noclip_check.setChecked(True)
                self.spectate_check.setChecked(True)
                self.chat_check.setChecked(True)
                self.props_check.setChecked(True)
                self.resource_check.setChecked(False)
                self.injection_check.setChecked(False)
                self.vpn_check.setChecked(False)
                self.explosion_check.setChecked(True)
                self.weapon_check.setChecked(True)
                
                # Load blacklists
                self.load_badger_blacklists()
                
            elif anticheat_name == "WaveShield":
                # Load WaveShield config
                self.noclip_check.setChecked(False)
                self.spectate_check.setChecked(True)
                self.chat_check.setChecked(True)
                self.props_check.setChecked(True)
                self.resource_check.setChecked(True)
                self.injection_check.setChecked(True)
                self.vpn_check.setChecked(True)
                self.explosion_check.setChecked(True)
                self.weapon_check.setChecked(True)
                
                # Load blacklists
                self.load_waveshield_blacklists()
                
            elif anticheat_name == "Dub Anticheat":
                # Load Dub anticheat config
                self.noclip_check.setChecked(False)
                self.spectate_check.setChecked(True)
                self.chat_check.setChecked(True)
                self.props_check.setChecked(True)
                self.resource_check.setChecked(True)
                self.injection_check.setChecked(True)
                self.vpn_check.setChecked(False)
                self.explosion_check.setChecked(True)
                self.weapon_check.setChecked(True)
                
                # Load blacklists
                self.load_dub_blacklists()
            
            self.load_ban_list()
            QMessageBox.information(self, "Success", f"Loaded {anticheat_name} configuration")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load anticheat config: {str(e)}")
            
    def load_badger_blacklists(self):
        """Load Badger anticheat blacklists"""
        # Clear existing lists
        self.props_list.clear()
        self.weapons_list.clear()
        
        # Add default blacklisted props
        props = [
            "prop_fnclink_05crnr1",
            "xs_prop_hamburgher_wl",
            "xs_prop_plastic_bottle_wl",
            "prop_windmill_01",
            "p_spinning_anus_s"
        ]
        self.props_list.addItems(props)
        
        # Add default blacklisted weapons
        weapons = [
            "WEAPON_RAILGUN",
            "WEAPON_GRENADELAUNCHER",
            "WEAPON_RPG",
            "WEAPON_MINIGUN"
        ]
        self.weapons_list.addItems(weapons)
        
    def load_waveshield_blacklists(self):
        """Load WaveShield blacklists"""
        # Clear existing lists
        self.props_list.clear()
        self.weapons_list.clear()
        
        # Add default blacklisted weapons
        weapons = [
            'WEAPON_GRENADELAUNCHER',
            'WEAPON_RPG',
            'WEAPON_STINGER',
            'WEAPON_MINIGUN',
            'WEAPON_RAILGUN',
            'WEAPON_RAYPISTOL'
        ]
        self.weapons_list.addItems(weapons)
        
    def load_dub_blacklists(self):
        """Load Dub anticheat blacklists"""
        # Clear existing lists
        self.props_list.clear()
        self.weapons_list.clear()
        
        # Add default blacklisted props
        props = [
            "prop_fnclink_05crnr1",
            "xs_prop_hamburgher_wl",
            "prop_windmill_01",
            "p_spinning_anus_s"
        ]
        self.props_list.addItems(props)
        
        # Add default blacklisted weapons
        weapons = [
            "WEAPON_SAWNOFFSHOTGUN",
            "WEAPON_BULLPUPSHOTGUN",
            "WEAPON_GRENADELAUNCHER",
            "WEAPON_RPG"
        ]
        self.weapons_list.addItems(weapons)
        
    def add_blacklist_item(self, item_type):
        """Add item to blacklist"""
        try:
            name, ok = QInputDialog.getText(
                self, f"Add {item_type.title()}", 
                f"Enter {item_type} name/hash:"
            )
            
            if ok and name:
                if item_type == "prop":
                    self.props_list.addItem(name)
                elif item_type == "weapon":
                    self.weapons_list.addItem(name)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add {item_type}: {str(e)}")
            
    def remove_blacklist_item(self, item_type):
        """Remove item from blacklist"""
        try:
            if item_type == "prop":
                current = self.props_list.currentItem()
                if current:
                    self.props_list.takeItem(self.props_list.row(current))
            elif item_type == "weapon":
                current = self.weapons_list.currentItem()
                if current:
                    self.weapons_list.takeItem(self.weapons_list.row(current))
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove {item_type}: {str(e)}")
            
    def export_config(self):
        """Export current configuration to file"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Configuration",
                f"{self.current_anticheat.replace(' ', '_').lower()}_config.json",
                "JSON Files (*.json)"
            )
            
            if filename:
                config = {
                    "anticheat": self.current_anticheat,
                    "components": {
                        "anti_noclip": self.noclip_check.isChecked(),
                        "anti_spectate": self.spectate_check.isChecked(),
                        "anti_fake_chat": self.chat_check.isChecked(),
                        "anti_props": self.props_check.isChecked(),
                        "resource_protection": self.resource_check.isChecked(),
                        "anti_injection": self.injection_check.isChecked(),
                        "anti_vpn": self.vpn_check.isChecked(),
                        "explosion_protection": self.explosion_check.isChecked(),
                        "weapon_protection": self.weapon_check.isChecked()
                    },
                    "detection_rules": {
                        "noclip": {
                            "trigger_count": self.noclip_count.value(),
                            "action": self.noclip_action.currentText()
                        },
                        "weapons": {
                            "detect_damage_mod": self.weapon_damage_check.isChecked(),
                            "detect_explosive": self.weapon_explosive_check.isChecked(),
                            "detect_infinite": self.weapon_infinite_check.isChecked()
                        }
                    },
                    "blacklists": {
                        "props": [self.props_list.item(i).text() for i in range(self.props_list.count())],
                        "weapons": [self.weapons_list.item(i).text() for i in range(self.weapons_list.count())]
                    },
                    "discord": {
                        "webhook_url": self.webhook_input.text(),
                        "log_detections": self.log_detections.isChecked(),
                        "log_kicks": self.log_kicks.isChecked(),
                        "log_bans": self.log_bans.isChecked()
                    }
                }
                
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=4)
                    
                QMessageBox.information(
                    self, "Success",
                    f"Configuration exported to {filename}"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export configuration: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CoresAI - Complete Trading & Server Management Suite")
        self.setMinimumSize(1200, 800)
        self._init_ui()
        
    def _init_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add header with logo
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        if os.path.exists(HEADER_IMAGE_PATH):
            pixmap = QPixmap(HEADER_IMAGE_PATH)
            scaled_pixmap = pixmap.scaled(200, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        
        # Add system status
        status_label = QLabel("System Status: Online")
        status_label.setStyleSheet("color: #00ff00;")
        header_layout.addWidget(status_label)
        layout.addLayout(header_layout)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #333333; }")
        
        # Add Crypto Trading tab
        crypto_tab = CryptoTab()
        tabs.addTab(crypto_tab, "Crypto Trading")
        
        # Add Server Management tabs
        for game_name, game_key in SERVER_GAMES:
            server_tab = ServerTab(game_name, game_key)
            tabs.addTab(server_tab, f"{game_name} Server")
        
        # Add AI Assistant tab
        ai_tab = AIAssistantTab()
        tabs.addTab(ai_tab, "AI Assistant")
        
        # Add Mining Pool tab
        pool_tab = CryptoPoolTab()
        tabs.addTab(pool_tab, "Mining Pools")
        
        # Add Friend Tracking tab
        friend_tab = FriendTrackingTab()
        tabs.addTab(friend_tab, "Friend Tracking")
        
        # Add Portfolio Management tab
        portfolio_tab = PortfolioTab()
        tabs.addTab(portfolio_tab, "Portfolio")
        
        # Add FiveM Anticheat tab
        fivem_anticheat_tab = FiveMAntiCheatTab()
        tabs.addTab(fivem_anticheat_tab, "FiveM Anticheat")
        
        layout.addWidget(tabs)
        
        # Add status bar
        self.statusBar().showMessage("Ready")
        
        # Set dark theme
        self.setStyleSheet(DARK_STYLE)
        
        # Start update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(5000)  # Update every 5 seconds
        
    def update_data(self):
        try:
            # Update system status
            response = requests.get(f"{API_URL}/status", timeout=5)
            if response.status_code == 200:
                self.statusBar().showMessage("Connected to backend services")
            else:
                self.statusBar().showMessage("Warning: Some services may be offline")
        except:
            self.statusBar().showMessage("Error: Cannot connect to backend services")

def main():
    app = QApplication(sys.argv)
    
    # Show splash screen
    if os.path.exists(SPLASH_IMAGE_PATH):
        splash_pix = QPixmap(SPLASH_IMAGE_PATH)
        splash = QSplashScreen(splash_pix)
        splash.show()
        app.processEvents()
        
        # Create and show main window after delay
        def show_main():
            window = MainWindow()
            window.show()
            splash.finish(window)
            
        QTimer.singleShot(SPLASH_DURATION, show_main)
    else:
        window = MainWindow()
        window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 