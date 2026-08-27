from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# Using bcrypt directly rather than passlib's bcrypt wrapper: passlib's
# CryptContext runs an internal self-test against a fixed string at import
# time that breaks under bcrypt>=4.1 (a known upstream incompatibility,
# unrelated to any password a real user would enter). Calling bcrypt
# directly avoids that self-test entirely. bcrypt has a hard 72-byte input
# limit, so long passwords are truncated to 72 bytes before hashing —
# document this if you ever raise a max-password-length rule in the UI.
_BCRYPT_MAX_BYTES = 72


def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8")[:_BCRYPT_MAX_BYTES], bcrypt.gensalt()).decode("utf-8")


def verify_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode("utf-8")[:_BCRYPT_MAX_BYTES], hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user: User) -> str:
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    if user.status == "suspended":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account suspended")
    return user


def require_role(*roles):
    def dep(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this action")
        return user
    return dep


# ---------------- simple in-memory rate limiter ----------------
# Sufficient for a single-process deployment. Swap for a Redis-backed limiter
# (e.g. slowapi + redis) once you run more than one worker.
_hits: dict[str, list[datetime]] = {}


def rate_limit(key_prefix: str, limit: int, window_minutes: int):
    def dep(request: Request):
        key = f"{key_prefix}:{request.client.host if request.client else 'unknown'}"
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=window_minutes)
        hits = [h for h in _hits.get(key, []) if h > window_start]
        if len(hits) >= limit:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many attempts — try again later.")
        hits.append(now)
        _hits[key] = hits
    return dep
