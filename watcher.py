import time
import sqlite3
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from scanner import backup_folder, IGNORE_DIRS, IGNORE_EXTENSIONS

# Watcher Configuration
DEBOUNCE_SECONDS = 3  # Wait time after last file modification before backing up

class BackupEventHandler(FileSystemEventHandler):
    def __init__(self, watch_path: Path):
        self.watch_path = watch_path
        self.last_event_time = 0
        self.pending_sync = False

    def on_any_event(self, event):
        # Ignore directory-only events
        if event.is_directory:
            return

        path = Path(event.src_path)

        # Ignore temporary, build, and vault files
        if any(part in IGNORE_DIRS for part in path.parts) or path.suffix.lower() in IGNORE_EXTENSIONS:
            return

        # Mark that a file change happened and record the timestamp
        self.last_event_time = time.time()
        self.pending_sync = True
        print(f"[EVENT] Change detected in {path.name} ({event.event_type})")

def start_watching(folder_to_watch: str):
    watch_path = Path(folder_to_watch).resolve()
    
    if not watch_path.exists():
        print(f"Error: Folder '{watch_path}' does not exist.")
        return

    event_handler = BackupEventHandler(watch_path)
    observer = Observer()
    observer.schedule(event_handler, path=str(watch_path), recursive=True)
    observer.start()

    print(f"\n==================================================")
    print(f"  Continuous Backup Active")
    print(f"  Watching: {watch_path}")
    print(f"  Debounce Window: {DEBOUNCE_SECONDS}s")
    print(f"==================================================")
    print("Press Ctrl+C to stop.\n")

    # Perform an initial scan on startup
    backup_folder(watch_path)

    try:
        while True:
            time.sleep(1)
            # Check if an event occurred and the debounce timer has expired
            if event_handler.pending_sync:
                time_since_last_event = time.time() - event_handler.last_event_time
                if time_since_last_event >= DEBOUNCE_SECONDS:
                    print("\n[SYNC] Changes settled. Triggering incremental backup...")
                    event_handler.pending_sync = False
                    backup_folder(watch_path)

    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping continuous backup service...")

    observer.join()

if __name__ == "__main__":
    FOLDER = input("Enter folder path to monitor continuously: ").strip()
    start_watching(FOLDER)