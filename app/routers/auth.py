from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
# from .. import schemas, crud, security, models
from schemas import Token, UserOut, UserCreate, LoginSchema
from models import User, RefreshToken
from core.database import get_db
from config import settings
from jose import jwt, JWTError
from datetime import datetime
from fastapi.responses import JSONResponse
from sqlalchemy import select
from crud import get_user_by_email, create_user,get_user_by_email,create_refresh_token, get_refresh_token_by_token, revoke_refresh_token
from security import verify_password, create_refresh_token_sec, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

# helper to set refresh cookie
def set_refresh_cookie(response: Response, token: str, expires_at: datetime):
    # cookie attributes: Secure + HttpOnly + SameSite=strict recommended for production (Secure requires https)
    # Max-Age in seconds:
    max_age = int((expires_at - datetime.utcnow()).total_seconds())
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=False,  # set True in production with HTTPS
        samesite="strict",
        max_age=max_age,
        path="/api/auth/refresh",
    )

@router.post("/register", response_model=UserOut)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    user = await create_user(db, data.name, data.email, data.password)
    return user

@router.post("/login", response_model=Token)
async def login(payload: LoginSchema, response: Response, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    at = create_access_token(user.id)
    rt = create_refresh_token_sec(user.id)

    # persist refresh token in DB
    await create_refresh_token(db, token=rt["token"], user_id=user.id, expires_at=rt["expires"], jti=rt["jti"])

    # set cookie
    set_refresh_cookie(response, rt["token"], rt["expires"])

    return {"access_token": at["token"], "expires_in": settings.ACCESS_TOKEN_EXPIRE_SECONDS}

@router.post("/refresh", response_model=Token)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    cookie = request.cookies.get("refresh_token")
    if not cookie:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = jwt.decode(cookie, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # check token in DB and not revoked
    stored = await get_refresh_token_by_token(db, cookie)
    if not stored or stored.revoked:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")

    # optionally check expiration (jose already did), but DB expiry may be used too

    # issue new access token (and optionally rotate refresh token)
    new_at = create_access_token(sub)
    return {"access_token": new_at["token"], "expires_in": settings.ACCESS_TOKEN_EXPIRE_SECONDS}

@router.post("/logout")
async def logout(response: Response, request: Request, db: AsyncSession = Depends(get_db)):
    cookie = request.cookies.get("refresh_token")
    if cookie:
        await revoke_refresh_token(db, cookie)
    # delete cookie
    response.delete_cookie("refresh_token", path="/api/auth/refresh")
    return JSONResponse({"detail": "Logged out"}, status_code=200)

# dependency to protect routes
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    q = await db.execute(select(User).where(User.id == user_id))
    user = q.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
