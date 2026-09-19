import threading
import time
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# Custom backup modules
from scanner import backup_folder
from watcher import start_watching
from server import run_server  # <--- Import your server runner

class BackupApp:
    def __init__(self):
        self.monitored_folder = None
        self.watcher_thread = None
        self.server_thread = None
        self.is_running = False
        self.status_message = "Idle"
        self.icon = None

    def create_tray_icon(self, color="blue"):
        image = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((4, 4, 60, 60), fill=color)
        draw.rectangle((24, 20, 40, 44), fill="white")
        return image

    def start_background_server(self):
        """Launches the FastAPI and mDNS server in a background daemon thread."""
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

    def select_folder(self):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        
        folder_selected = filedialog.askdirectory(title="Select Folder to Continuously Back Up")
        root.destroy()

        if folder_selected:
            self.monitored_folder = folder_selected
            self.status_message = f"Watching: {Path(folder_selected).name}"
            self.update_tray()
            messagebox.showinfo("Backup Vault", f"Selected folder:\n{folder_selected}\n\nStarting continuous backup...")
            self.restart_watcher()

    def run_manual_scan(self):
        if not self.monitored_folder:
            messagebox.showwarning("Backup Vault", "Please select a folder to back up first!")
            return
        threading.Thread(target=self._manual_scan_worker, daemon=True).start()

    def _manual_scan_worker(self):
        self.status_message = "Syncing..."
        self.icon.icon = self.create_tray_icon("orange")
        backup_folder(self.monitored_folder)
        self.status_message = f"Watching: {Path(self.monitored_folder).name}"
        self.icon.icon = self.create_tray_icon("green")

    def restart_watcher(self):
        if self.monitored_folder:
            self.is_running = True
            self.icon.icon = self.create_tray_icon("green")
            
            self.watcher_thread = threading.Thread(
                target=start_watching, 
                args=(self.monitored_folder,), 
                daemon=True
            )
            self.watcher_thread.start()

    def quit_app(self, icon, item):
        self.is_running = False
        icon.stop()
        sys.exit(0)

    def get_status_text(self, item):
        return f"Status: {self.status_message}"

    def update_tray(self):
        if self.icon:
            self.icon.update_menu()

    def setup_tray(self):
        # 1. Start the HTTP/mDNS server
        self.start_background_server()

        # 2. Build the system tray menu
        menu = pystray.Menu(
            item(self.get_status_text, lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item("Select Folder to Back Up...", lambda: self.select_folder()),
            item("Run Manual Sync Now", lambda: self.run_manual_scan()),
            pystray.Menu.SEPARATOR,
            item("Exit Backup Vault", self.quit_app)
        )

        self.icon = pystray.Icon(
            "LocalBackupVault",
            self.create_tray_icon("blue"),
            "Local Backup Vault",
            menu
        )

app = BackupApp()

if __name__ == "__main__":
    app.setup_tray()
    app.icon.run()