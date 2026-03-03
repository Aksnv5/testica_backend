from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from config import settings
from typing import Dict, Any
import uuid

pwd_ctx = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_access_token(sub: int, extra: Dict[str, Any] = None) -> Dict[str, Any]:
    now = datetime.utcnow()
    exp = now + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    payload = {"sub": str(sub), "exp": exp, "iat": now, "jti": str(uuid.uuid4())}
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return {"token": token, "expires": exp}

def create_refresh_token_sec(sub: int) -> Dict[str, Any]:
    now = datetime.utcnow()
    exp = now + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    payload = {"sub": str(sub), "exp": exp, "iat": now, "jti": str(uuid.uuid4())}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return {"token": token, "expires": exp, "jti": payload["jti"]}
