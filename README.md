# Local Backup Vault 

A privacy-focused, zero-cloud local backup engine for Windows and Mobile. Automatically monitors local directories for real-time file synchronization, manages content-addressable deduplicated storage via SHA-256, and runs an mDNS-enabled REST API server to receive seamless background backups from mobile devices over Wi-Fi.

---

##  Core Features

- **Continuous File System Monitoring:** Instant real-time change tracking powered by `watchdog`.
- **SHA-256 Content Deduplication:** Block-level storage engine powered by SQLite. Duplicate files share physical chunk references to save disk space.
- **Auto-Discovery Server:** Integrated mDNS (`zeroconf`) service broadcasting over local Wi-Fi (`_backupvault._tcp.local.`).
- **Mobile Backup REST API:** FastAPI & Uvicorn asynchronous endpoints streaming incoming mobile photos/videos directly into the local vault.
- **System Tray Integration:** Built-in status indicators and tray controls via `pystray`.
- **Portable Distribution:** Single-file standalone executable created via PyInstaller and wrapped into a native Windows Installer via Inno Setup 6.

---

##  System Architecture

```text
  ┌────────────────────────────────────────────────────────┐
  │                    Local Network                       │
  └───────────────────────────┬────────────────────────────┘
                              │
                    mDNS Auto-Discovery
                    (_backupvault._tcp)
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │                Windows System Tray App                 │
  │               (LocalBackupVault.exe)                   │
  │                                                        │
  │   ┌────────────────────┐      ┌────────────────────┐   │
  │   │   FastAPI Server   │      │ File System Watch  │   │
  │   │  (Mobile Sync API) │      │  (watchdog engine) │   │
  │   └─────────┬──────────┘      └─────────┬──────────┘   │
  └─────────────┼───────────────────────────┼──────────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                     SHA-256 Deduplication
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │                   Storage Vault                        │
  │      D:\LocalBackupVault\                              │
  │      ├── database.db (SQLite Index)                    │
  │      └── chunks/     (Deduplicated Blocks)             │
  └────────────────────────────────────────────────────────┘
