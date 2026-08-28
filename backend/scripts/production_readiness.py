"""Pre-deployment self-checks. Does not claim external services are healthy."""
from pathlib import Path
import os

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=[".env.example","requirements.txt"]
FORBIDDEN=[".env"]

def run():
    errors=[]
    for name in REQUIRED:
        if not (ROOT/name).exists(): errors.append(f"missing {name}")
    for name in FORBIDDEN:
        if (ROOT/name).exists(): errors.append(f"secret file present: {name}")
    if not os.getenv("ORGANIZER_EMAIL"): print("WARN: SMTP env not configured in this shell")
    if errors: raise SystemExit("; ".join(errors))
    print("Static production readiness checks passed")

if __name__ == "__main__": run()
