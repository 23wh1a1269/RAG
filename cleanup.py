#!/usr/bin/env python3
"""Cleanup script to remove unnecessary files and optimize storage."""
import os
import shutil
from pathlib import Path

def cleanup():
    """Remove backup files and orphaned data."""
    
    # Files to remove
    backup_files = [
        "main_backup.py",
        "auth_backup.py", 
        "email_service_backup.py",
        "migrate_users.py",
        "backend.log",
    ]
    
    removed = []
    for file in backup_files:
        path = Path(file)
        if path.exists():
            path.unlink()
            removed.append(file)
            print(f"✓ Removed: {file}")
    
    # Clean orphaned PDFs in uploads root
    uploads = Path("uploads")
    if uploads.exists():
        for item in uploads.iterdir():
            if item.is_file() and item.suffix == ".pdf":
                item.unlink()
                removed.append(str(item))
                print(f"✓ Removed orphaned PDF: {item.name}")
    
    # Clean __pycache__
    for pycache in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache)
        print(f"✓ Removed: {pycache}")
    
    # Clean .pyc files
    for pyc in Path(".").rglob("*.pyc"):
        pyc.unlink()
        print(f"✓ Removed: {pyc}")
    
    print(f"\n✅ Cleanup complete! Removed {len(removed)} items.")

if __name__ == "__main__":
    cleanup()
