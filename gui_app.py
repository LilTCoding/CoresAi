import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys
import os
import requests
import soundfile as sf
import sounddevice as sd
import cv2
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox, QSplashScreen,
    QTabWidget, QListWidget, QFileDialog, QSplitter, QInputDialog, QDialog, QComboBox, QTextBrowser
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QPoint

API_URL = "http://localhost:8080/api/v1/chat"
HEADER_IMAGE_PATH = "header_image.png"
SPLASH_IMAGE_PATH = "dragon_logo.png"
SPLASH_DURATION = 2500  # milliseconds

SERVER_GAMES = [
    ("FiveM QB", "fivem_qb"),
    ("Minecraft", "minecraft"),
    ("Arma Reforger", "arma_reforger"),
    ("Rust", "rust")
]

HEAD_IMAGE_PATH = "ai_facedetect_head.png"

class ServerTab(QWidget):
    def __init__(self, game_name, game_key):
        super().__init__()
        self.game_name = game_name
        self.game_key = game_key
        self.current_subdir = ""
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        # Server controls
        controls_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Unknown")
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.restart_btn = QPushButton("Restart")
        self.start_btn.clicked.connect(self.start_server)
        self.stop_btn.clicked.connect(self.stop_server)
        self.restart_btn.clicked.connect(self.restart_server)
        controls_layout.addWidget(self.status_label)
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(self.restart_btn)
        layout.addLayout(controls_layout)

        # Mod/Plugin management section
        mod_layout = QHBoxLayout()
        self.mod_list = QListWidget()
        self.refresh_mods_btn = QPushButton("Refresh Mods/Plugins")
        self.refresh_mods_btn.clicked.connect(self.refresh_mod_list)
        self.add_mod_btn = QPushButton("Add Mod/Plugin")
        self.add_mod_btn.clicked.connect(self.add_mod)
        self.remove_mod_btn = QPushButton("Remove Selected")
        self.remove_mod_btn.clicked.connect(self.remove_mod)
        self.suggest_mods_btn = QPushButton("AI Suggest Mods/Plugins")
        self.suggest_mods_btn.clicked.connect(self.suggest_mods)
        mod_btns_layout = QVBoxLayout()
        mod_btns_layout.addWidget(self.refresh_mods_btn)
        mod_btns_layout.addWidget(self.add_mod_btn)
        mod_btns_layout.addWidget(self.remove_mod_btn)
        mod_btns_layout.addWidget(self.suggest_mods_btn)
        mod_layout.addWidget(QLabel("Mods/Plugins:"))
        mod_layout.addWidget(self.mod_list)
        mod_layout.addLayout(mod_btns_layout)
        layout.addLayout(mod_layout)

        # Splitter for file browser and editor
        splitter = QSplitter(Qt.Horizontal)
        # File browser with buttons
        file_browser_layout = QVBoxLayout()
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_file_or_navigate)
        file_btn_layout = QHBoxLayout()
        self.up_btn = QPushButton("Up")
        self.up_btn.clicked.connect(self.go_up)
        self.new_file_btn = QPushButton("New File")
        self.new_file_btn.clicked.connect(self.create_file)
        self.new_folder_btn = QPushButton("New Folder")
        self.new_folder_btn.clicked.connect(self.create_folder)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_selected)
        file_btn_layout.addWidget(self.up_btn)
        file_btn_layout.addWidget(self.new_file_btn)
        file_btn_layout.addWidget(self.new_folder_btn)
        file_btn_layout.addWidget(self.delete_btn)
        file_browser_layout.addWidget(self.file_list)
        file_browser_layout.addLayout(file_btn_layout)
        file_browser_widget = QWidget()
        file_browser_widget.setLayout(file_browser_layout)
        splitter.addWidget(file_browser_widget)
        # Notepad/editor
        editor_layout = QVBoxLayout()
        self.editor = QTextEdit()
        editor_btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save File")
        self.save_btn.clicked.connect(self.save_file)
        self.ai_edit_btn = QPushButton("AI Edit File")
        self.ai_edit_btn.clicked.connect(self.ai_edit_file)
        editor_btn_layout.addWidget(self.save_btn)
        editor_btn_layout.addWidget(self.ai_edit_btn)
        editor_widget = QWidget()
        editor_widget.setLayout(editor_btn_layout)
        editor_layout.addWidget(self.editor)
        editor_layout.addWidget(editor_widget)
        editor_container = QWidget()
        editor_container.setLayout(editor_layout)
        splitter.addWidget(editor_container)
        splitter.setSizes([200, 450])
        layout.addWidget(splitter)

        # AI chat area
        chat_layout = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText(f"Ask {self.game_name} AI...")
        self.chat_input.returnPressed.connect(self.ask_ai)
        self.chat_send_btn = QPushButton("Ask AI")
        self.chat_send_btn.clicked.connect(self.ask_ai)
        chat_input_layout.addWidget(self.chat_input)
        chat_input_layout.addWidget(self.chat_send_btn)
        chat_layout.addWidget(self.chat_display)
        chat_layout.addLayout(chat_input_layout)
        layout.addLayout(chat_layout)

        self.setLayout(layout)
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

    def load_file_or_navigate(self, item):
        filename = item.text()
        if filename.endswith("/"):
            # Directory navigation
            self.current_subdir = os.path.join(self.current_subdir, filename[:-1])
            self.refresh_file_list()
            return
        try:
            resp = requests.post("http://localhost:8080/api/v1/read-file", json={"game": self.game_key, "filepath": os.path.join(self.current_subdir, filename)})
            if resp.status_code == 200:
                self.editor.setPlainText(resp.json().get("content", ""))
            else:
                self.editor.setPlainText(f"[Error: {resp.text}]")
        except Exception as e:
            self.editor.setPlainText(f"[Error: {str(e)}]")

    def save_file(self):
        current_item = self.file_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No file selected", "Please select a file to save.")
            return
        filename = current_item.text()
        content = self.editor.toPlainText()
        try:
            resp = requests.post("http://localhost:8080/api/v1/write-file", json={"game": self.game_key, "filepath": filename, "content": content})
            if resp.status_code == 200:
                QMessageBox.information(self, "Saved", f"File '{filename}' saved.")
            else:
                QMessageBox.warning(self, "Error", f"Failed to save file: {resp.text}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save file: {e}")

    def refresh_status(self):
        try:
            resp = requests.post("http://localhost:8080/api/v1/server-status", json={"game": self.game_key})
            if resp.status_code == 200:
                status = resp.json().get("status", "Unknown")
                self.status_label.setText(f"Status: {status}")
            else:
                self.status_label.setText(f"Status: [Error]")
        except Exception:
            self.status_label.setText(f"Status: [Error]")

    def start_server(self):
        requests.post("http://localhost:8080/api/v1/start-server", json={"game": self.game_key})
        self.refresh_status()

    def stop_server(self):
        requests.post("http://localhost:8080/api/v1/stop-server", json={"game": self.game_key})
        self.refresh_status()

    def restart_server(self):
        requests.post("http://localhost:8080/api/v1/restart-server", json={"game": self.game_key})
        self.refresh_status()

    def ask_ai(self):
        user_text = self.chat_input.text().strip()
        if not user_text:
            return
        self.chat_display.append(f"<b>You:</b> {user_text}")
        self.chat_input.clear()
        try:
            resp = requests.post(API_URL, json={"text": user_text, "use_voice": False})
            if resp.status_code == 200:
                ai_reply = resp.json().get("response", "[No reply]")
                self.chat_display.append(f"<b>AI:</b> {ai_reply}")
            else:
                self.chat_display.append(f"<b>AI:</b> [Error: {resp.text}]")
        except Exception as e:
            self.chat_display.append(f"<b>AI:</b> [Error: {str(e)}]")

    def go_up(self):
        if self.current_subdir:
            self.current_subdir = os.path.dirname(self.current_subdir)
            self.refresh_file_list()

    def create_file(self):
        name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and name:
            path = os.path.join(self.current_subdir, name)
            requests.post("http://localhost:8080/api/v1/write-file", json={"game": self.game_key, "filepath": path, "content": ""})
            self.refresh_file_list()

    def create_folder(self):
        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and name:
            path = os.path.join(self.current_subdir, name)
            # Create a dummy file to make the folder (backend will need to support this)
            requests.post("http://localhost:8080/api/v1/write-file", json={"game": self.game_key, "filepath": os.path.join(path, ".keep"), "content": ""})
            self.refresh_file_list()

    def delete_selected(self):
        current_item = self.file_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No file selected", "Please select a file or folder to delete.")
            return
        filename = current_item.text().rstrip("/")
        path = os.path.join(self.current_subdir, filename)
        requests.post("http://localhost:8080/api/v1/delete-file", json={"game": self.game_key, "filepath": path})
        self.refresh_file_list()

    def refresh_mod_list(self):
        self.mod_list.clear()
        # For demonstration, just list files in a typical mods/plugins/resources folder
        folder_map = {
            "minecraft": "plugins",
            "fivem_qb": "resources",
            "arma_reforger": "addons",
            "rust": "oxide/plugins"
        }
        mod_folder = folder_map.get(self.game_key, "plugins")
        try:
            resp = requests.post("http://localhost:8080/api/v1/list-files", json={"game": self.game_key, "subdir": mod_folder})
            if resp.status_code == 200:
                for item in resp.json().get("items", []):
                    self.mod_list.addItem(item["name"])
        except Exception:
            self.mod_list.addItem("[Error loading mods/plugins]")

    def add_mod(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Mod/Plugin File")
        if file_path:
            folder_map = {
                "minecraft": "plugins",
                "fivem_qb": "resources",
                "arma_reforger": "addons",
                "rust": "oxide/plugins"
            }
            mod_folder = folder_map.get(self.game_key, "plugins")
            filename = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                content = f.read()
            # For now, just create an empty file (backend upload endpoint can be added for real upload)
            requests.post("http://localhost:8080/api/v1/write-file", json={"game": self.game_key, "filepath": os.path.join(mod_folder, filename), "content": ""})
            self.refresh_mod_list()

    def remove_mod(self):
        current_item = self.mod_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No mod/plugin selected", "Please select a mod/plugin to remove.")
            return
        folder_map = {
            "minecraft": "plugins",
            "fivem_qb": "resources",
            "arma_reforger": "addons",
            "rust": "oxide/plugins"
        }
        mod_folder = folder_map.get(self.game_key, "plugins")
        filename = current_item.text()
        requests.post("http://localhost:8080/api/v1/delete-file", json={"game": self.game_key, "filepath": os.path.join(mod_folder, filename)})
        self.refresh_mod_list()

    def suggest_mods(self):
        desc, ok = QInputDialog.getText(self, "AI Suggest Mods/Plugins", "Describe your server or what you want:")
        if ok and desc:
            try:
                resp = requests.post("http://localhost:8080/api/v1/suggest-mods", json={"game": self.game_key, "description": desc})
                if resp.status_code == 200:
                    mods = resp.json().get("suggested_mods", [])
                    QMessageBox.information(self, "AI Suggestions", f"Suggested Mods/Plugins:\n{chr(10).join(mods)}")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to get suggestions: {resp.text}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to get suggestions: {e}")

    def ai_edit_file(self):
        current_item = self.file_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No file selected", "Please select a file to AI edit.")
            return
        filename = current_item.text().rstrip("/")
        path = os.path.join(self.current_subdir, filename)
        instruction, ok = QInputDialog.getText(self, "AI Edit File", "Describe what you want to change:")
        if ok and instruction:
            try:
                resp = requests.post("http://localhost:8080/api/v1/ai-file-edit", json={"game": self.game_key, "filepath": path, "instruction": instruction})
                if resp.status_code == 200:
                    new_content = resp.json().get("new_content", "")
                    self.editor.setPlainText(new_content)
                    QMessageBox.information(self, "AI Edit", "File updated by AI.")
                else:
                    QMessageBox.warning(self, "Error", f"AI edit failed: {resp.text}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"AI edit failed: {e}")

class CreateServerWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Server Wizard")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Game:"))
        self.game_combo = QComboBox()
        for game_name, game_key in SERVER_GAMES:
            self.game_combo.addItem(game_name, game_key)
        layout.addWidget(self.game_combo)
        layout.addWidget(QLabel("Describe your server (features, mods, etc.):"))
        self.desc_input = QTextEdit()
        layout.addWidget(self.desc_input)
        self.generate_btn = QPushButton("Generate Blueprint")
        self.generate_btn.clicked.connect(self.generate_blueprint)
        layout.addWidget(self.generate_btn)
        self.result_browser = QTextBrowser()
        layout.addWidget(self.result_browser)
        self.setLayout(layout)

    def generate_blueprint(self):
        game_key = self.game_combo.currentData()
        desc = self.desc_input.toPlainText().strip()
        if not desc:
            self.result_browser.setText("Please enter a description.")
            return
        self.result_browser.setText("Generating blueprint... Please wait.")
        try:
            resp = requests.post("http://localhost:8080/api/v1/generate-blueprint", json={"game": game_key, "description": desc})
            if resp.status_code == 200:
                data = resp.json()
                plan = data.get("ai_plan", "[No plan]")
                mods = data.get("suggested_mods", [])
                tips = data.get("setup_tips", "")
                result = f"<b>AI Plan:</b><br>{plan}<br><br><b>Suggested Mods/Plugins:</b><br>{', '.join(mods)}<br><br><b>Setup Tips:</b><br>{tips}"
                self.result_browser.setHtml(result)
            else:
                self.result_browser.setText(f"[Error: {resp.text}]")
        except Exception as e:
            self.result_browser.setText(f"[Error: {str(e)}]")

class FaceTrackerThread(QThread):
    positionChanged = pyqtSignal(int, int)  # dx, dy relative to center

    def __init__(self, camera_index: int = 0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self._running = True
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def run(self):
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        # Lower resolution for faster processing
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        if not cap.isOpened():
            return

        while self._running:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces):
                (x, y, w, h) = faces[0]
                face_center_x = x + w // 2
                face_center_y = y + h // 2
                frame_h, frame_w = gray.shape
                dx = face_center_x - frame_w // 2
                dy = face_center_y - frame_h // 2
                self.positionChanged.emit(dx, dy)
            time.sleep(0.15)

        cap.release()

    def stop(self):
        self._running = False
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CoresAI Game Server Manager")
        self.setGeometry(100, 100, 900, 700)
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        # Header image
        header_label = QLabel()
        if os.path.exists(HEADER_IMAGE_PATH):
            pixmap = QPixmap(HEADER_IMAGE_PATH)
            header_label.setPixmap(pixmap.scaledToWidth(300, Qt.SmoothTransformation))
            header_label.setAlignment(Qt.AlignCenter)
        else:
            header_label.setText("CoresAI")
            header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # AI Head label (overlays header area)
        self.ai_head_label = QLabel(central_widget)
        if os.path.exists(HEAD_IMAGE_PATH):
            head_pix = QPixmap(HEAD_IMAGE_PATH)
            self.ai_head_label.setPixmap(head_pix.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.ai_head_label.setFixedSize(120, 120)
        self.ai_head_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.ai_head_label.show()
        # Will position later in resizeEvent

        # Create Server button
        self.create_server_btn = QPushButton("Create Server (AI Wizard)")
        self.create_server_btn.clicked.connect(self.open_create_server_wizard)
        layout.addWidget(self.create_server_btn)
        # Tabs
        self.tabs = QTabWidget()
        for game_name, game_key in SERVER_GAMES:
            self.tabs.addTab(ServerTab(game_name, game_key), game_name)
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)

        # Start face tracker
        self.face_tracker = FaceTrackerThread()
        self.face_tracker.positionChanged.connect(self.on_face_position)
        self.face_tracker.start()

    def open_create_server_wizard(self):
        dlg = CreateServerWizard(self)
        dlg.exec_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Center the head label in the window
        win_w = self.width()
        self.ai_head_label.move((win_w - self.ai_head_label.width()) // 2, 60)

    def on_face_position(self, dx, dy):
        # Map dx,dy to small movement of head label
        factor = 0.1  # sensitivity
        new_x = (self.width() - self.ai_head_label.width()) // 2 + int(dx * factor)
        new_y = 60 + int(dy * factor)
        # Clamp within window bounds
        new_x = max(0, min(self.width() - self.ai_head_label.width(), new_x))
        new_y = max(0, min(self.height() - self.ai_head_label.height(), new_y))
        self.ai_head_label.move(new_x, new_y)

    def closeEvent(self, event):
        try:
            self.face_tracker.stop()
        except Exception:
            pass
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    def show_main():
        print("[DEBUG] Showing main window...")
        window = MainWindow()
        window.show()
    # Splash screen
    if os.path.exists(SPLASH_IMAGE_PATH):
        print("[DEBUG] Showing splash screen...")
        splash_pix = QPixmap(SPLASH_IMAGE_PATH)
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.show()
        QTimer.singleShot(SPLASH_DURATION, splash.close)
        QTimer.singleShot(SPLASH_DURATION, show_main)
    else:
        show_main()
    sys.exit(app.exec_()) 