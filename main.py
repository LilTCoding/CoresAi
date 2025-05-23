"""
CoresAI Main Entry Point
"""

import tkinter as tk
from tkinter import ttk, messagebox

class CoresAILauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CoresAI")
        self.root.geometry("400x300")
        self.setup_ui()
        
    def setup_ui(self):
        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="Welcome to CoresAI").grid(row=0, column=0, pady=10)
        ttk.Button(frame, text="Launch", command=self.launch).grid(row=1, column=0, pady=20)
        
    def launch(self):
        messagebox.showinfo("CoresAI", "Starting CoresAI...")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CoresAILauncher()
    app.run() 