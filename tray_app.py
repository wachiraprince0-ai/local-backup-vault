import threading
import time
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# Import our custom backup modules
from scanner import backup_folder
from watcher import start_watching

# Application State
class BackupApp:
    def __init__(self):
        self.monitored_folder = None
        self.watcher_thread = None
        self.is_running = False
        self.status_message = "Idle"
        self.icon = None

    def create_tray_icon(self, color="blue"):
        """Generates a dynamic 64x64 icon for the system tray."""
        image = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        # Draw a colored circle background with an inner symbol
        draw.ellipse((4, 4, 60, 60), fill=color)
        draw.rectangle((24, 20, 40, 44), fill="white")  # Simple inner vault symbol
        return image

    def select_folder(self):
        """Opens a native Windows directory picker dialog."""
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
        """Triggers an immediate scan without waiting for the watcher timer."""
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
        """Starts the background watchdog thread for continuous sync."""
        if self.monitored_folder:
            self.is_running = True
            self.icon.icon = self.create_tray_icon("green")
            
            # Run watcher in a background daemon thread
            self.watcher_thread = threading.Thread(
                target=start_watching, 
                args=(self.monitored_folder,), 
                daemon=True
            )
            self.watcher_thread.start()

    def quit_app(self, icon, item):
        """Cleanly stops the tray icon and exits."""
        self.is_running = False
        icon.stop()
        sys.exit(0)

    def get_status_text(self, item):
        return f"Status: {self.status_message}"

    def update_tray(self):
        if self.icon:
            self.icon.update_menu()

    def setup_tray(self):
        # Define System Tray Right-Click Menu
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
    print("Local Backup Vault System Tray App is running near your system clock.")
    app.icon.run()