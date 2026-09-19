import os
import hashlib
import sqlite3
import shutil
from pathlib import Path

# Paths
VAULT_PATH = Path("D:/LocalBackupVault").resolve()
DB_PATH = VAULT_PATH / "database.db"
CHUNKS_PATH = VAULT_PATH / "chunks"
TMP_PATH = VAULT_PATH / ".tmp"

# Folders and file extensions to ignore completely
IGNORE_DIRS = {".tmp", "chunks", "snapshots", "$RECYCLE.BIN", "System Volume Information", ".git"}
IGNORE_EXTENSIONS = {".db", ".db-wal", ".db-shm", ".tmp"}

def calculate_file_hash(file_path: Path) -> str:
    """Reads a file in 1MB blocks and generates a SHA-256 fingerprint."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(1024 * 1024):  # 1MB buffer
            hasher.update(chunk)
    return hasher.hexdigest()

def backup_folder(source_folder: Path):
    source_folder = Path(source_folder).resolve()
    
    if not source_folder.exists():
        print(f"Error: Source folder '{source_folder}' does not exist.")
        return

    # Safety Check: Prevent the vault from backing up itself
    if source_folder == VAULT_PATH or VAULT_PATH in source_folder.parents:
        print("❌ Error: You cannot back up the vault directory itself!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"\nScanning source folder: {source_folder}")
    
    for root, dirs, files in os.walk(source_folder):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for filename in files:
            file_path = Path(root) / filename

            if file_path.suffix.lower() in IGNORE_EXTENSIONS:
                continue

            relative_path = str(file_path.relative_to(source_folder))
            
            try:
                stat = file_path.stat()
                size_bytes = stat.st_size
                mtime_unix = int(stat.st_mtime)
            except OSError as e:
                print(f"[SKIP] Permission/IO error on {relative_path}: {e}")
                continue

            # Check if file was already scanned and unchanged
            cursor.execute(
                "SELECT file_hash FROM files WHERE relative_path = ? AND mtime_unix = ? AND size_bytes = ?",
                (relative_path, mtime_unix, size_bytes)
            )
            existing = cursor.fetchone()

            if existing:
                print(f"[SKIP] Unchanged: {relative_path}")
                continue

            # Calculate fingerprint
            print(f"[HASHING] {relative_path}...")
            file_hash = calculate_file_hash(file_path)

            # Deduplication check
            cursor.execute("SELECT storage_path FROM chunks WHERE chunk_hash = ?", (file_hash,))
            chunk_exists = cursor.fetchone()

            if not chunk_exists:
                subfolder = CHUNKS_PATH / file_hash[:2]
                subfolder.mkdir(parents=True, exist_ok=True)
                
                target_file = subfolder / f"{file_hash}.dat"
                tmp_file = TMP_PATH / f"{file_hash}.tmp"

                shutil.copy2(file_path, tmp_file)
                tmp_file.rename(target_file)

                cursor.execute(
                    "INSERT INTO chunks (chunk_hash, size_bytes, storage_path, ref_count) VALUES (?, ?, ?, 1)",
                    (file_hash, size_bytes, str(target_file))
                )
                print(f"  [+] Stored new data -> {target_file.name}")
            else:
                cursor.execute(
                    "UPDATE chunks SET ref_count = ref_count + 1 WHERE chunk_hash = ?",
                    (file_hash,)
                )
                print(f"  [✓] Duplicate content found! Reused existing stored block.")

            cursor.execute("""
                INSERT INTO files (relative_path, size_bytes, mtime_unix, file_hash)
                VALUES (?, ?, ?, ?)
            """, (relative_path, size_bytes, mtime_unix, file_hash))

            conn.commit()

    conn.close()
    print("\nScan and backup completed successfully!")