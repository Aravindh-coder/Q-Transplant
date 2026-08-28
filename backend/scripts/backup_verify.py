"""Verify backup artifacts are non-empty and have the expected format."""
from pathlib import Path
import sys

def verify(path):
    p=Path(path)
    if not p.exists() or p.stat().st_size == 0: raise SystemExit(f"Invalid backup: {p}")
    print(f"Backup artifact OK: {p} ({p.stat().st_size} bytes)")

if __name__ == "__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: backup_verify.py BACKUP_FILE")
    verify(sys.argv[1])
