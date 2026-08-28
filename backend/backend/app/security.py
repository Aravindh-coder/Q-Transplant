from datetime import datetime, timedelta, timezone
import hashlib
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User, RevokedToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
_BCRYPT_MAX_BYTES = 72

def hash_password(pw: str) -> str:
    if len(pw.encode("utf-8")) > _BCRYPT_MAX_BYTES:
        raise ValueError("Password is too long; maximum is 72 UTF-8 bytes.")
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode("utf-8")[:_BCRYPT_MAX_BYTES], hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False

def token_fingerprint(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def create_access_token(user: User) -> str:
    payload = {"sub": user.id, "email": user.email, "role": user.role,
               "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_MINUTES)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    fingerprint = token_fingerprint(token)
    if db.query(RevokedToken).filter(RevokedToken.token_jti == fingerprint).first():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token has been revoked")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    if user.status in ("suspended", "inactive"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is not active")
    return user

def require_role(*roles):
    def dep(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized for this action")
        return user
    return dep

_hits: dict[str, list[datetime]] = {}
def rate_limit(key_prefix: str, limit: int, window_minutes: int):
    def dep(request: Request):
        key = f"{key_prefix}:{request.client.host if request.client else 'unknown'}"
        now = datetime.now(timezone.utc)
        start = now - timedelta(minutes=window_minutes)
        hits = [h for h in _hits.get(key, []) if h > start]
        if len(hits) >= limit:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many attempts — try again later.")
        hits.append(now)
        _hits[key] = hits
    return dep
