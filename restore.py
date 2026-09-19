import sqlite3
import shutil
from pathlib import Path

VAULT_PATH = Path("D:/LocalBackupVault").resolve()
DB_PATH = VAULT_PATH / "database.db"

def list_backed_up_files():
    """Lists all files recorded in the vault database."""
    if not DB_PATH.exists():
        print("Error: Vault database not found!")
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT f.id, f.relative_path, f.size_bytes, f.file_hash, c.storage_path
        FROM files f
        JOIN chunks c ON f.file_hash = c.chunk_hash
    """)
    records = cursor.fetchall()
    conn.close()
    return records

def restore_all(destination_dir: Path):
    """Reconstructs all files from chunks into the target restore folder."""
    destination_dir = Path(destination_dir).resolve()
    destination_dir.mkdir(parents=True, exist_ok=True)

    records = list_backed_up_files()
    if not records:
        print("No files found in vault to restore.")
        return

    print(f"\nRestoring {len(records)} file(s) to: {destination_dir}\n")

    for file_id, relative_path, size_bytes, file_hash, storage_path in records:
        chunk_file = Path(storage_path)
        target_restore_path = destination_dir / relative_path

        if not chunk_file.exists():
            print(f"[ERROR] Missing chunk for {relative_path} ({chunk_file})")
            continue

        # Ensure parent directories exist
        target_restore_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy data block back to original file layout
        shutil.copy2(chunk_file, target_restore_path)
        print(f"[RESTORED] {relative_path} -> {target_restore_path}")

    print("\nRestore completed successfully!")

if __name__ == "__main__":
    records = list_backed_up_files()
    if not records:
        print("No files stored in vault database.")
    else:
        print("=== Files Currently in Backup Vault ===")
        for _, path, size, hash_val, _ in records:
            print(f"- {path} ({size} bytes) | Hash: {hash_val[:12]}...")

        print("\n" + "="*40)
        RESTORE_TARGET = input("Enter path where you want to restore these files (e.g., C:/Users/wachi/Desktop/RestoredFiles): ").strip()
        if RESTORE_TARGET:
            restore_all(RESTORE_TARGET)