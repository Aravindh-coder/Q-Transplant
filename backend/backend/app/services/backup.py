"""Production backup strategy helpers. Execute from a protected scheduler/worker."""
import os
import shutil
from datetime import datetime, timezone


def backup_database(source: str, destination_dir: str) -> str:
    os.makedirs(destination_dir, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = os.path.join(destination_dir, f"qtransplant-{stamp}.db")
    shutil.copy2(source, target)
    return target


def backup_documents(source_dir: str, destination_dir: str) -> str:
    os.makedirs(destination_dir, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = os.path.join(destination_dir, f"documents-{stamp}")
    shutil.copytree(source_dir, target, dirs_exist_ok=True)
    return target
