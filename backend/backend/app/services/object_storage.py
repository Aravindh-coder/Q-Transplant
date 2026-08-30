"""Object storage for uploaded documents (doctor photos/certificates,
hospital licenses, donor/patient medical documents).

Render's local disk is ephemeral -- anything written to it is wiped on
the next deploy or restart. Without this, every uploaded document is
silently lost the first time the service redeploys, which breaks the
doctor approval workflow entirely (the organizer has nothing to review).

Works with any S3-compatible provider: AWS S3, Cloudflare R2, Backblaze
B2, MinIO, etc. -- set S3_ENDPOINT_URL for anything that isn't AWS.

If S3_BUCKET isn't configured, every function here falls back to the
local filesystem so the app keeps working in development (and keeps
working on Render too, just with the ephemeral-storage caveat documented
in README_DEPLOYMENT.md).
"""
import os
from pathlib import Path
from typing import Optional

S3_BUCKET = os.environ.get("S3_BUCKET", "")
S3_REGION = os.environ.get("S3_REGION", "auto")
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL") or None
S3_ACCESS_KEY_ID = os.environ.get("S3_ACCESS_KEY_ID", "")
S3_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY", "")

LOCAL_ROOT = Path(os.getenv("UPLOAD_DIR", "uploads")).resolve()
_S3_PREFIX = "s3://"


def is_configured() -> bool:
    return bool(S3_BUCKET and S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY)


def _client():
    import boto3
    return boto3.client(
        "s3",
        region_name=S3_REGION,
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY_ID,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY,
    )


def save(key: str, data: bytes, content_type: str) -> str:
    """Stores the file and returns a storage reference to persist on the
    Document row (either 's3://<key>' or a local filesystem path)."""
    if is_configured():
        _client().put_object(Bucket=S3_BUCKET, Key=key, Body=data, ContentType=content_type)
        return _S3_PREFIX + key
    path = LOCAL_ROOT / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return str(path)


def read(storage_ref: str) -> bytes:
    """Reads a file back given whatever save() returned for it."""
    if storage_ref.startswith(_S3_PREFIX):
        key = storage_ref[len(_S3_PREFIX):]
        obj = _client().get_object(Bucket=S3_BUCKET, Key=key)
        return obj["Body"].read()
    return Path(storage_ref).read_bytes()


def presigned_url(storage_ref: str, expires_seconds: int = 300) -> Optional[str]:
    """Returns a short-lived direct URL for S3-backed files, or None for
    locally-stored files (caller should stream those itself instead)."""
    if not storage_ref.startswith(_S3_PREFIX):
        return None
    key = storage_ref[len(_S3_PREFIX):]
    return _client().generate_presigned_url("get_object", Params={"Bucket": S3_BUCKET, "Key": key}, ExpiresIn=expires_seconds)


def exists(storage_ref: str) -> bool:
    if storage_ref.startswith(_S3_PREFIX):
        key = storage_ref[len(_S3_PREFIX):]
        try:
            _client().head_object(Bucket=S3_BUCKET, Key=key)
            return True
        except Exception:
            return False
    return Path(storage_ref).is_file()
